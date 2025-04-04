import { supabase } from '../../../supabase/init.js';
import { currentUser } from '../auth.js';
import { getProjectId } from '../app.js';

// Initialize file upload component
function initFileUpload(options) {
  const container = document.getElementById(options.container);
  if (!container) return null;
  
  // Set up options
  const config = {
    bucket: options.bucket || 'attachments',
    path: options.path || '',
    allowedTypes: options.allowedTypes || [],
    maxFileSize: options.maxFileSize || 10 * 1024 * 1024, // Default: 10MB
    maxFiles: options.maxFiles || null,
    onUploadComplete: options.onUploadComplete || null,
    recordId: options.recordId || null,
    recordType: options.recordType || null,
    module: options.module || null,
    dropzoneOptions: options.dropzoneOptions || {}
  };
  
  // Store configuration in container
  container.dataset.config = JSON.stringify(config);
  
  // Initialize Dropzone
  const dropzoneElement = container.querySelector('.dropzone');
  if (!dropzoneElement) return null;
  
  // Create Dropzone instance
  const dropzone = new Dropzone(dropzoneElement, {
    url: '/file-upload', // Will be overridden in custom handler
    autoProcessQueue: false,
    addRemoveLinks: true,
    maxFilesize: config.maxFileSize / (1024 * 1024), // Convert to MB
    maxFiles: config.maxFiles,
    acceptedFiles: config.allowedTypes.length ? config.allowedTypes.join(',') : null,
    dictDefaultMessage: 'Drop files here or click to upload',
    dictFallbackMessage: 'Your browser does not support drag and drop file uploads.',
    dictFileTooBig: 'File is too big ({{filesize}}MB). Max file size: {{maxFilesize}}MB.',
    dictInvalidFileType: 'You cannot upload files of this type.',
    dictResponseError: 'Server responded with {{statusCode}} code.',
    dictCancelUpload: 'Cancel upload',
    dictUploadCanceled: 'Upload canceled.',
    dictRemoveFile: 'Remove file',
    dictMaxFilesExceeded: 'You cannot upload any more files.',
    dictFileSizeUnits: {tb: 'TB', gb: 'GB', mb: 'MB', kb: 'KB', b: 'b'},
    ...config.dropzoneOptions
  });
  
  // Override the default sendFile method to use Supabase Storage
  dropzone.uploadFiles = function(files) {
    // Process each file
    const promises = files.map(file => processFile(file, config));
    
    // Handle completion
    Promise.all(promises)
      .then(results => {
        // Trigger onUploadComplete callback
        if (config.onUploadComplete && typeof config.onUploadComplete === 'function') {
          config.onUploadComplete(results.filter(result => result !== null));
        }
        
        // Clear queue
        this.removeAllFiles(true);
      })
      .catch(error => {
        console.error('Error uploading files:', error);
        showUploadError(container, 'Failed to upload one or more files');
      });
  };
  
  // Set up event listeners
  setupDropzoneListeners(dropzone, container);
  
  // Return the Dropzone instance for further customization
  return dropzone;
}

// Process a file upload
async function processFile(file, config) {
  try {
    // Update file status
    file.status = Dropzone.UPLOADING;
    file.upload.progress = 0;
    file.upload.bytesSent = 0;
    file.upload.total = file.size;
    
    // Generate unique file name
    const timestamp = new Date().getTime();
    const fileExtension = file.name.split('.').pop();
    const fileName = `${config.recordType || 'file'}_${config.recordId || timestamp}_${timestamp}.${fileExtension}`;
    const filePath = config.path ? `${config.path}/${fileName}` : fileName;
    
    // Upload file to Supabase Storage
    const { data, error } = await supabase.storage
      .from(config.bucket)
      .upload(filePath, file, {
        cacheControl: '3600',
        upsert: false
      });
    
    if (error) throw error;
    
    // Update progress
    file.upload.progress = 100;
    file.upload.bytesSent = file.size;
    
    // Get public URL
    const { data: urlData } = await supabase.storage
      .from(config.bucket)
      .getPublicUrl(filePath);
    
    const publicUrl = urlData.publicUrl;
    
    // If record tracking is enabled, record the file in database
    if (config.recordId && config.recordType && config.module) {
      await recordFileUpload(file, config, publicUrl, filePath);
    }
    
    // Update file status
    file.status = Dropzone.SUCCESS;
    
    // Return file info
    return {
      name: file.name,
      size: file.size,
      type: file.type,
      path: filePath,
      url: publicUrl
    };
  } catch (error) {
    console.error('Error processing file:', error);
    
    // Update file status
    file.status = Dropzone.ERROR;
    file.upload.error = error.message || 'Upload failed';
    
    return null;
  }
}

// Record file upload in database
async function recordFileUpload(file, config, fileUrl, filePath) {
  try {
    // Insert record in attachments table
    const { error } = await supabase
      .from('attachments')
      .insert({
        record_id: config.recordId,
        record_type: config.recordType,
        module: config.module,
        file_name: file.name,
        file_type: file.type,
        file_size: file.size,
        file_url: fileUrl,
        file_path: filePath,
        bucket: config.bucket,
        created_by: currentUser.id,
        created_at: new Date().toISOString(),
        project_id: getProjectId()
      });
    
    if (error) throw error;
    
    // Log activity
    await logFileActivity('upload', config.recordId, config.recordType, config.module);
    
    return true;
  } catch (error) {
    console.error('Error recording file upload:', error);
    return false;
  }
}

// Log file activity
async function logFileActivity(action, recordId, recordType, module) {
  try {
    await supabase
      .from('activity_log')
      .insert({
        action,
        module,
        record_type: recordType,
        record_id: recordId,
        user_id: currentUser.id,
        created_at: new Date().toISOString(),
        project_id: getProjectId()
      });
  } catch (error) {
    console.error('Error logging file activity:', error);
  }
}

// Set up Dropzone event listeners
function setupDropzoneListeners(dropzone, container) {
  // File added
  dropzone.on('addedfile', function(file) {
    // Hide any previous errors
    hideUploadError(container);
    
    // Check file size
    const config = JSON.parse(container.dataset.config);
    if (file.size > config.maxFileSize) {
      this.removeFile(file);
      showUploadError(container, `File is too large. Maximum size is ${formatFileSize(config.maxFileSize)}.`);
      return;
    }
    
    // Check file type if restrictions are set
    if (config.allowedTypes.length > 0) {
      const fileExtension = file.name.split('.').pop().toLowerCase();
      let isAllowed = false;
      
      for (const type of config.allowedTypes) {
        if (type.includes('/*')) {
          // Handle wildcards like 'image/*'
          const mainType = type.split('/')[0];
          if (file.type.startsWith(mainType)) {
            isAllowed = true;
            break;
          }
        } else if (type.startsWith('.')) {
          // Handle extension like '.pdf'
          if (`.${fileExtension}` === type) {
            isAllowed = true;
            break;
          }
        } else {
          // Handle full MIME type like 'application/pdf'
          if (file.type === type) {
            isAllowed = true;
            break;
          }
        }
      }
      
      if (!isAllowed) {
        this.removeFile(file);
        showUploadError(container, 'File type not allowed.');
        return;
      }
    }
  });
  
  // All files added
  dropzone.on('complete', function(file) {
    // Check if all files are processed
    if (this.getQueuedFiles().length === 0 && this.getUploadingFiles().length === 0) {
      // All uploads finished
      const successCount = this.getFilesWithStatus(Dropzone.SUCCESS).length;
      const errorCount = this.getFilesWithStatus(Dropzone.ERROR).length;
      
      if (errorCount > 0) {
        showUploadError(container, `${errorCount} file(s) failed to upload.`);
      } else if (successCount > 0) {
        showUploadSuccess(container, `${successCount} file(s) uploaded successfully.`);
      }
    }
  });
  
  // Upload button clicked
  const uploadButton = container.querySelector('.upload-button');
  if (uploadButton) {
    uploadButton.addEventListener('click', () => {
      if (dropzone.getQueuedFiles().length > 0) {
        dropzone.processQueue();
      } else {
        showUploadError(container, 'No files selected for upload.');
      }
    });
  }
  
  // Cancel button clicked
  const cancelButton = container.querySelector('.cancel-button');
  if (cancelButton) {
    cancelButton.addEventListener('click', () => {
      dropzone.removeAllFiles(true);
      hideUploadError(container);
    });
  }
}

// Format file size for display
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Show upload error
function showUploadError(container, message) {
  const errorElement = container.querySelector('.upload-error');
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = 'block';
  }
}

// Hide upload error
function hideUploadError(container) {
  const errorElement = container.querySelector('.upload-error');
  if (errorElement) {
    errorElement.style.display = 'none';
  }
}

// Show upload success
function showUploadSuccess(container, message) {
  const successElement = container.querySelector('.upload-success');
  if (successElement) {
    successElement.textContent = message;
    successElement.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
      successElement.style.display = 'none';
    }, 5000);
  }
}

// Export
export {
  initFileUpload
};