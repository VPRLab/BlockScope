import os


ethereum_repo_dir = '/Users/xiao/PyCharmProjects/BlockScopeCodebase/EthereumForks'

origin_repo = os.path.join(ethereum_repo_dir, 'go-ethereum')

target_repos = {
    'Binance': os.path.join(ethereum_repo_dir, 'bsc'),
    'Optimism': os.path.join(ethereum_repo_dir, 'optimism'),
    'Polygon': os.path.join(ethereum_repo_dir, 'bor'),
    'Avalanche': os.path.join(ethereum_repo_dir, 'subnet-evm'),
    'Celo': os.path.join(ethereum_repo_dir, 'celo-blockchain'),
}

patches = [
    {
        # 0
        # CVE-2022-29177
        # Mar 8, 2022
        # https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-29177
        # https://github.com/ethereum/go-ethereum/pull/24507
        # Crash when handling specially crafted p2p messages sent from an attacker node
        'sha': '870b4505a05cd8b3604078ed4afcd3012bf72a47',
        'file': 'p2p/peer.go',
        'add_info': (337, 339),
        'del_info': (335, 339),
        'up_info': None,
        'down_info': None
    },

    {
        # 1
        # CVE-2021-41173
        # Sep 29, 2021
        # https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-41173
        # https://github.com/ethereum/go-ethereum/pull/23657
        # DoS via malicious snap/1 request
        'sha': '3a6fe69f2356c50d1819be3417fcb89abc6e9cfe',
        'file': 'trie/trie.go',
        'add_info': (179, 182),
        'del_info': None,
        'up_info': True,
        'down_info': True
    },

    {
        # 2
        # CVE-2021-39137
        # Aug 24, 2021
        # https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-39137
        # https://github.com/ethereum/go-ethereum/pull/23381
        # RETURNDATA corruption via datacopy
        'sha': '1d995731923ca899964371ddb213d40b7e773818',
        'file': 'core/vm/instructions.go',
        'add_info': (672, 672),
        'del_info': None,
        'up_info': True,
        'down_info': True
    },

    {
        # 3
        # CVE-2020-26265
        # Aug 21, 2020
        # https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-26265
        # https://github.com/ethereum/go-ethereum/pull/21080
        # Consensus flaw during block processing
        'sha': '87c0ba92136a75db0ab2aba1046d4a9860375d6a',
        'file': 'core/state/statedb.go',
        'add_info': (590, 593),
        'del_info': (592, 592),
        'up_info': True,
        'down_info': None
    },

    {
        # 4
        # CVE-2020-26264
        # Nov 24, 2020
        # https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-26264
        # https://github.com/ethereum/go-ethereum/pull/21896
        # LES Server DoS via GetProofsV2
        'sha': 'bddd103a9f0af27ef533f04e06ea429cf76b6d46',
        'file': 'les/server_handler.go',
        'add_info': (654, 654),
        'del_info': None,
        'up_info': None,
        'down_info': True
    },

    {
        # 5
        # CVE-2020-26240
        # Nov 12, 2020
        # https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-26240
        # https://github.com/ethereum/go-ethereum/pull/21793
        # Miners to create invalid PoW
        'sha': 'd990df909d7839640143344e79356754384dcdd0',
        'file': 'consensus/ethash/algorithm.go',
        'add_info': (316, 316),
        'del_info': (316, 316),
        'up_info': None,
        'down_info': None
    },

]
