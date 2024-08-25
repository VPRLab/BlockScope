import os

from inputs_bitcoin import bitcoin_repo_dir
from inputs_ethereum import ethereum_repo_dir

S_SIM_THRESHOLD = 0.25
F_SIM_THRESHOLD = 0.35
CODE_SIM_WEIGHT = 0.95

CONTEXT_LINES = 4

ENDS_TUPLE = (',', '=', '|', '&', '+', '-', '*', '/', '(')

COMMON_KEYWORDS = {'.tostring', 'tostring', 'uint8_t', 'uint32_t', 'uint64_t', 'uint256'}

REPO_GITHUB = {
    os.path.join(bitcoin_repo_dir, 'bitcoin'): 'bitcoin/bitcoin',
    os.path.join(bitcoin_repo_dir, 'dogecoin'): 'dogecoin/dogecoin',
    os.path.join(bitcoin_repo_dir, 'bitcoin-abc'): 'Bitcoin-ABC/bitcoin-abc',
    os.path.join(bitcoin_repo_dir, 'litecoin'): 'litecoin-project/litecoin',
    os.path.join(bitcoin_repo_dir, 'bitcoin-sv'): 'bitcoin-sv/bitcoin-sv',
    os.path.join(bitcoin_repo_dir, 'dash'): 'dashpay/dash',
    os.path.join(bitcoin_repo_dir, 'zcash'): 'zcash/zcash',
    os.path.join(bitcoin_repo_dir, 'BTCGPU'): 'BTCGPU/BTCGPU',
    os.path.join(bitcoin_repo_dir, 'zen'): 'HorizenOfficial/zen',
    os.path.join(bitcoin_repo_dir, 'qtum'): 'qtumproject/qtum',
    os.path.join(bitcoin_repo_dir, 'digibyte'): 'digibyte/digibyte',
    os.path.join(bitcoin_repo_dir, 'Ravencoin'): 'RavenProject/Ravencoin',
    os.path.join(ethereum_repo_dir, 'go-ethereum'): 'ethereum/go-ethereum',
    os.path.join(ethereum_repo_dir, 'bsc'): 'bnb-chain/bsc',
    os.path.join(ethereum_repo_dir, 'optimism'): 'ethereum-optimism/optimism',
    os.path.join(ethereum_repo_dir, 'bor'): 'maticnetwork/bor',
    os.path.join(ethereum_repo_dir, 'subnet-evm'): 'ava-labs/subnet-evm',
    os.path.join(ethereum_repo_dir, 'go-aoa'): 'aurorachain-io/go-aoa',
    os.path.join(ethereum_repo_dir, 'celo-blockchain'): 'celo-org/celo-blockchain',
}

DRIVER_PATH = ''

GITHUB_TOKEN = ''

CALC_DELAY = False

IS_BITCOIN = True
