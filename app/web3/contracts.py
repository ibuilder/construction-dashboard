from web3 import Web3

class ContractManager:
    def __init__(self, contract_address, abi, provider_url):
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)

    def get_project(self, project_id):
        return self.contract.functions.getProject(project_id).call()

    def create_project(self, name, description, account):
        tx_hash = self.contract.functions.createProject(name, description).transact({'from': account})
        return self.web3.eth.waitForTransactionReceipt(tx_hash)

    def update_project(self, project_id, name, description, account):
        tx_hash = self.contract.functions.updateProject(project_id, name, description).transact({'from': account})
        return self.web3.eth.waitForTransactionReceipt(tx_hash)

    def delete_project(self, project_id, account):
        tx_hash = self.contract.functions.deleteProject(project_id).transact({'from': account})
        return self.web3.eth.waitForTransactionReceipt(tx_hash)

    def get_all_projects(self):
        return self.contract.functions.getAllProjects().call()