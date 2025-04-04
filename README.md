# Construction Project Management Dashboard

A comprehensive web-based dashboard for managing construction projects with multiple modules covering all aspects of project management from preconstruction to closeout.

## Features

- **Multi-role Access Control**: Different access levels for Owners, Owner's Representatives, General Contractors, Subcontractors, and Design Team members
- **Comprehensive Modules**: Covers Preconstruction, Engineering, Field, Safety, Contracts, Cost Management, BIM, and Closeout
- **CRUD Operations**: Create, Read, Update, and Delete functionality for all modules
- **Commenting System**: Users can comment on any record
- **Exportable Records**: Export any record to PDF
- **Sortable and Filterable Tables**: Easy data management with advanced filtering
- **Responsive Design**: Works on desktop and mobile devices
- **Supabase Integration**: Cloud-based PostgreSQL database with built-in authentication

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **CSS Framework**: Bootstrap 5
- **JavaScript Libraries**: 
  - jQuery for DOM manipulation
  - DataTables for enhanced tables
  - Chart.js for data visualization
  - jsPDF for PDF generation
  - Dropzone.js for file uploads
  - FullCalendar for scheduling
- **Backend**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **File Storage**: Supabase Storage

## Project Structure

```
construction-dashboard/
├── assets/
│   ├── css/
│   │   ├── style.css
│   │   └── vendor/
│   │       ├── bootstrap.min.css
│   │       ├── dataTables.bootstrap5.min.css
│   │       └── ... (other vendor CSS)
│   ├── js/
│   │   ├── app.js
│   │   ├── auth.js
│   │   ├── modules/
│   │   │   ├── preconstruction.js
│   │   │   ├── engineering.js
│   │   │   ├── field.js
│   │   │   ├── safety.js
│   │   │   ├── contracts.js
│   │   │   ├── cost.js
│   │   │   ├── bim.js
│   │   │   ├── closeout.js
│   │   │   ├── settings.js
│   │   │   └── reports.js
│   │   ├── components/
│   │   │   ├── comments.js
│   │   │   ├── pdf-export.js
│   │   │   ├── file-upload.js
│   │   │   └── ... (other components)
│   │   └── vendor/
│   │       ├── jquery.min.js
│   │       ├── bootstrap.bundle.min.js
│   │       ├── chart.min.js
│   │       ├── jspdf.min.js
│   │       └── ... (other vendor JS)
│   └── img/
│       ├── logo.png
│       ├── icons/
│       └── ... (other images)
├── pages/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── preconstruction/
│   │   ├── qualified-bidders.html
│   │   ├── bid-packages.html
│   │   └── bid-manual.html
│   ├── engineering/
│   │   ├── rfis.html
│   │   ├── submittals.html
│   │   ├── drawings.html
│   │   ├── specifications.html
│   │   ├── file-explorer.html
│   │   ├── permitting.html
│   │   ├── meeting-minutes.html
│   │   └── transmittals.html
│   ├── field/
│   │   ├── daily-reports.html
│   │   ├── photo-library.html
│   │   ├── schedule.html
│   │   ├── checklists.html
│   │   ├── punchlist.html
│   │   └── pull-planning.html
│   ├── safety/
│   │   ├── observations.html
│   │   ├── pretask-plans.html
│   │   ├── job-hazard-analysis.html
│   │   └── employee-orientations.html
│   ├── contracts/
│   │   ├── prime-contract.html
│   │   ├── subcontracts.html
│   │   ├── professional-service-agreements.html
│   │   ├── lien-waivers.html
│   │   ├── certificates-of-insurance.html
│   │   └── letters-of-intent.html
│   ├── cost/
│   │   ├── budget-forecast.html
│   │   ├── invoicing.html
│   │   ├── direct-costs.html
│   │   ├── potential-changes.html
│   │   ├── change-orders.html
│   │   ├── approval-letters.html
│   │   └── time-materials.html
│   ├── bim/
│   │   ├── 3d-model.html
│   │   └── coordination-issues.html
│   ├── closeout/
│   │   ├── om-manuals.html
│   │   ├── warranties.html
│   │   └── attic-stock.html
│   ├── settings/
│   │   ├── project-info.html
│   │   ├── csi-divisions.html
│   │   ├── cost-codes.html
│   │   ├── labor-rates.html
│   │   ├── material-rates.html
│   │   ├── equipment-rates.html
│   │   ├── companies.html
│   │   ├── users.html
│   │   ├── project-help.html
│   │   └── database-settings.html
│   └── reports/
│       ├── generate.html
│       └── templates.html
└── supabase/
    └── init.js
```

## Installation and Setup

1. Clone the repository
```
git clone https://github.com/yourusername/construction-dashboard.git
cd construction-dashboard
```

2. Create a Supabase project at [Supabase](https://supabase.com)

3. Update the Supabase configuration in `supabase/init.js` with your project URL and anonymous key

4. Run the initial database setup scripts (provided in the repository)

5. Serve the application using a local web server
```
# Using Python
python -m http.server

# Using Node.js
npx serve
```

6. Navigate to `http://localhost:8000` (or whatever port your server is using)

## Supabase Database Setup

The database structure includes tables for each module with appropriate relationships. Key tables include:

- Users
- Projects
- Companies
- Roles
- Permissions
- Comments
- And specific tables for each module's data

The full database schema is defined in the SQL scripts in the repository.

## User Roles and Permissions

The system supports the following user roles with different permission levels:

1. **Owner**: Full access to all modules and administrative functions
2. **Owner's Representative**: Access to most modules with approval capabilities
3. **General Contractor**: Access to project management modules with create/edit permissions
4. **Subcontractor**: Limited access to specific modules related to their work
5. **Design Team**: Access to design-related modules with limited permissions for other areas

## Deployment

For production deployment:

1. Build optimization:
   - Minify all CSS and JavaScript files
   - Optimize images
   - Enable gzip compression

2. Deploy to a web hosting service or cloud provider of your choice (AWS, Azure, Netlify, Vercel, etc.)

3. Set up appropriate security measures:
   - Enable HTTPS
   - Configure proper CORS settings
   - Set up regular backups

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please open an issue on GitHub or contact support@constructiondashboard.com