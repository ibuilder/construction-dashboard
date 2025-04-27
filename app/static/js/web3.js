// This file contains JavaScript code for interacting with Web3 functionalities.

let web3;
let contract;

async function initWeb3() {
    if (window.ethereum) {
        web3 = new Web3(window.ethereum);
        try {
            await window.ethereum.request({ method: 'eth_requestAccounts' });
            console.log('Ethereum account connected');
        } catch (error) {
            console.error('User denied account access', error);
        }
    } else {
        console.log('Non-Ethereum browser detected. You should consider trying MetaMask!');
    }
}

async function initContract(contractAddress, abi) {
    contract = new web3.eth.Contract(abi, contractAddress);
}

async function getAccount() {
    const accounts = await web3.eth.getAccounts();
    return accounts[0];
}

async function sendTransaction(method, params) {
    const account = await getAccount();
    return contract.methods[method](...params).send({ from: account });
}

async function callMethod(method, params) {
    return contract.methods[method](...params).call();
}

window.addEventListener('load', async () => {
    await initWeb3();
});

// Export functions for use in other modules
export { initContract, sendTransaction, callMethod };