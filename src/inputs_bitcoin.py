import os


bitcoin_repo_dir = '/Users/xiao/PyCharmProjects/BlockScopeCodebase/BitcoinForks'

origin_repo = os.path.join(bitcoin_repo_dir, 'bitcoin')

target_repos = {
    'Dogecoin': os.path.join(bitcoin_repo_dir, 'dogecoin'),
    'Bitcoin Cash': os.path.join(bitcoin_repo_dir, 'bitcoin-abc'),
    'Litecoin': os.path.join(bitcoin_repo_dir, 'litecoin'),
    'Bitcoin SV': os.path.join(bitcoin_repo_dir, 'bitcoin-sv'),
    'Dash': os.path.join(bitcoin_repo_dir, 'dash'),
    'Zcash': os.path.join(bitcoin_repo_dir, 'zcash'),
    'Bitcoin Gold': os.path.join(bitcoin_repo_dir, 'BTCGPU'),
    'Horizen': os.path.join(bitcoin_repo_dir, 'zen'),
    'Qtum': os.path.join(bitcoin_repo_dir, 'qtum'),
    'DigiByte': os.path.join(bitcoin_repo_dir, 'digibyte'),
    'Ravencoin': os.path.join(bitcoin_repo_dir, 'Ravencoin'),
}

patches = [
    {
        # 0
        'sha': '2fb9c1e6681370478e24a19172ed6d78d95d50d3',
        'file': 'src/wallet/wallet.cpp',
        'add_info': (2986, 3003),
        'del_info': None,
        'up_info': None,
        'down_info': True
    },

    {
        # 1
        # Check that new headers are not a descendant of an invalid block
        # https://github.com/bitcoin/bitcoin/pull/11531
        'sha': '015a5258adffb0cf394f387a95ac9c8afc34cfc3',
        'file': 'src/validation.cpp',
        'add_info': (3107, 3121),
        'del_info': None,
        'up_info': True,
        'down_info': None
    },

    {
        # 2
        # check the aborted nodes
        # Shut down if a corrupted block is found in ConnectBlock().
        # This prevents an infinite loop trying to connect such a block,
        # and alerts the node operator that there may be potential hardware failure.
        # https://github.com/bitcoin/bitcoin/pull/12561
        # https://github.com/bitcoin/bitcoin/commit/0e7c52dc6cbb8fd881a0dd57a6167a812fe71dc4
        'sha': '0e7c52dc6cbb8fd881a0dd57a6167a812fe71dc4',
        'file': 'src/validation.cpp',
        'add_info': (1794, 1800),
        'del_info': (1794, 1794),
        'up_info': None,
        'down_info': True
    },

    {
        # 3
        # add timeout check for sync header
        # https://github.com/dogecoin/dogecoin/issues/2282
        'sha': '76f74811c44b5119d5c19364b0594d423248ac0e',
        'file': 'src/net_processing.cpp',
        'add_info': (2889, 2889),
        'del_info': None,
        'up_info': True,
        'down_info': None
    },

    {
        # 4
        # Disconnect outbound peers relaying invalid headers
        # https://github.com/bitcoin/bitcoin/commit/37886d5e2f9992678dea4b1bd893f4f10d61d3ad
        'sha': '37886d5e2f9992678dea4b1bd893f4f10d61d3ad',
        'file': 'src/net_processing.cpp',
        'add_info': (1261, 1261),
        'del_info': (1261, 1262),
        'up_info': None,
        'down_info': None
    },

    {
        # 5
        # CVE-2019-15947
        # https://github.com/bitcoin/bitcoin/issues/16824
        # https://github.com/bitcoin/bitcoin/pull/15600
        'sha': 'd831831822885717e9841f1ff67c19add566fa45',
        'file': 'src/support/lockedpool.cpp',
        'add_info': (253, 255),
        'del_info': None,
        'up_info': True,
        'down_info': None
    },

    {
        # 6
        # CVE-2018-17145
        # https://github.com/bitcoin/bitcoin/pull/13622
        # Vulnerable function inventory created at
        # https://github.com/bitcoin/bitcoin/commit/e8ef3da7133dd9fc411fa8b3cc8b8fc2f9c58a98
        # Commited time Jun 27, 2011
        'sha': 'beef7ec4be725beea870a2da510d2817487601ec',
        'file': 'src/net_processing.cpp',
        'func': 'processgetdata',
        'del_info': (1267, 1269),
        'add_info': None,
        'up_info': True,
        'down_info': None
    },

    {
        # 7
        # CVE-2021-3401
        # https://github.com/bitcoin/bitcoin/pull/16578
        # First included in Bitcoin:
        # https://github.com/achow101/bitcoin/commit/202d853bbea8ecb2164b9c9dc69e2129b45f05f8
        'sha': 'a2714a5c69f0b0506689af04c3e785f71ee0915d',
        'file': 'src/qt/bitcoin.cpp',
        'add_info': (172, 176),
        'del_info': (172, 173),
        'up_info': None,
        'down_info': True
    },

    {
        # 8
        # https://github.com/bitcoin/bitcoin/pull/17906
        # keywords: It just fixes a race condition during a qt test that was observed on travis:
        # vuln introduction commit:ce14345a89dfa05992f8d2c7c9fe36315d4a67e6
        # time: 14 Oct 2013
        'sha': '8313fa8e8112e429e104b7e7fd48e5e6e359b82e',
        'file': 'src/net.h',
        'add_info': (389, 390),
        'del_info': (389, 390),
        'up_info': None,
        'down_info': None
    },

    {
        # 9
        # https://github.com/bitcoin/bitcoin/pull/16512
        # This PR changes that all the inputs and outputs are shuffled in the joined transaction.
        'sha': '6f405a1d3b38395e35571b68aae55cae50e0762a',
        'file': 'src/rpc/rawtransaction.cpp',
        'func': 'joinpsbts',
        'add_info': (1631, 1631),
        'del_info': (1608, 1608),
        'up_info': None,
        'down_info': None
    },

    {
        # 10
        # https://github.com/bitcoin/bitcoin/pull/17621
        # This plugs the privacy leak detailed at #17605, at least for the single-key case.
        'sha': '09502452bbbe21bb974f1de8cf53196373921ab9',
        'file': 'src/wallet/wallet.cpp',
        'func': 'IsSpentKey',
        'add_info': (727, 748),
        'del_info': (732, 732),
        'up_info': None,
        'down_info': None
    },

    {
        # 11
        # https://github.com/bitcoin/bitcoin/pull/16796
        # Warning! Segmentation Fault is a critical error for security.
        # Source: Fix segmentation fault in CreateWalletFromFile
        # But this commit just changed one line in the source code, wondering for checking results.
        'sha': 'fa734603b78ba31ebf0da5d2dbe87386eafff01a',
        'file': 'src/wallet/wallet.cpp',
        'add_info': (4246, 4246),
        'del_info': (4246, 4246),
        'up_info': None,
        'down_info': None
    },

    {
        # 12
        # https://github.com/bitcoin/bitcoin/pull/16557
        'sha': '214c4ecb9ab306627a08abb35cf82c73f10ec627',
        'file': 'src/wallet/wallet.cpp',
        'add_info': (2163, 2165),
        'del_info': None,
        'up_info': True,
        'down_info': None
    },

    {
        # 13
        # https://github.com/bitcoin/bitcoin/pull/16152
        # BIP 37 bloom filters have been well-known to be a significant DoS
        # target for some time. However, in order to provide continuity for
        # SPV clients relying on it, the NODE_BLOOM service flag was added,
        # and left as a default, to ensure sufficient nodes exist with such a
        # flag.
        # introduction commit:
        # https://github.com/TheBlueMatt/bitcoin/commit/1fb91b3496f2f07bbace1f9f8e716f7f62d889e6
        # time: 11 Feb 2016
        'sha': '5efcb772838e404ca5757818d5548efcb872724b',
        'file': 'src/validation.h',
        'add_info': (130, 130),
        'del_info': (130, 130),
        'up_info': None,
        'down_info': None
    },

    {
        # 14
        # https://github.com/bitcoin/bitcoin/pull/15834
        # Fix a bug in NOTFOUND processing, where the in-flight map for a peer was keeping transactions it shouldn't
        'sha': '308b76732f97020c86977e29c854e8e27262cf7c',
        'file': 'src/net_processing.cpp',
        'add_info': (4001, 4002),
        'del_info': (3990, 3990),
        'up_info': None,
        'down_info': None
    },

    {
        # 15
        # https://github.com/bitcoin/bitcoin/pull/15582
        'sha': 'c9963ae8b1a4d26d19c58e18fde9c85783edb788',
        'file': 'src/rpc/rawtransaction.cpp',
        'add_info': (1984, 1985),
        'del_info': (1984, 1985),
        'up_info': None,
        'down_info': None
    },

    {
        # 16
        # https://github.com/bitcoin/bitcoin/pull/15337/
        # rpc: Fix for segfault if combinepsbt called with empty inputs
        'sha': '30d0f7be6e6bd45fed7195ddf31187438b02227a',
        'file': 'src/rpc/rawtransaction.cpp',
        'func': 'combinepsbt',
        'add_info': (1517, 1518),
        'del_info': None,
        'up_info': None,
        'down_info': True
    },

    {
        # 17
        # https://github.com/bitcoin/bitcoin/pull/15323/
        # Expose g_is_mempool_loaded via getmempoolinfo
        # fix a race condition in mempool_persist.py:
        # Introduce commit
        # https://github.com/Empact/bitcoin/commit/cb1e319fe9e198c9c5cf5236fe9af5a3d748b9e8
        # Fixed issue, https://github.com/bitcoin/bitcoin/issues/12863#issuecomment-381031762
        # Fixed a race condition found in text `mempool_persist.py`
        # time: Mar 29, 2018
        'sha': 'effe81f7503d2ca3c88cfdea687f9f997f353e0d',
        'file': 'src/init.cpp',
        'func': 'shutdown',
        'add_info': (238, 239),
        'del_info': (238, 239),
        'up_info': None,
        'down_info': None
    },

    {
        # 18
        # cve-2018-17144
        # https://github.com/bitcoin/bitcoin/pull/14249
        'sha': 'b8f801964f59586508ea8da6cf3decd76bc0e571',
        'file': 'src/validation.cpp',
        'func': 'checkblock',
        'add_info': (3125, 3125),
        'del_info': (3125, 3125),
        'up_info': None,
        'down_info': None
    },

    {
        # 19
        # https://github.com/bitcoin/bitcoin/pull/15305
        # Crash if disconnecting a block fails
        # Fix issue: https://github.com/bitcoin/bitcoin/issues/14341
        'sha': '4433ed0f730cfd60eeba3694ff3c283ce2c0c8ee',
        'file': 'src/validation.cpp',
        'func': 'ActivateBestChainStep',
        'add_info': (2554, 2558),
        'del_info': None,
        'up_info': True,
        'down_info': None
    },

    {
        # 20
        # https://github.com/bitcoin/bitcoin/pull/15235
        # Do not import private keys to wallets with private keys disabled
        'sha': 'e6c58d3b014ab8ef5cca4be68764af4b79685fcb',
        'file': 'src/wallet/rpcdump.cpp',
        'func': 'importwallet',
        'add_info': (623, 627),
        'del_info': None,
        'up_info': None,
        'down_info': True
    },

    {
        # 21
        # https://github.com/bitcoin/bitcoin/pull/15039
        # wallet: Avoid leaking nLockTime fingerprint when anti-fee-sniping,
        # introduce commit:
        # https://github.com/MarcoFalke/bitcoin-core/commit/ba7fcc8de06602576ab6a5911879d3d8df80d36a
        # Oct 13, 2014
        'sha': 'fa48baf23eb2ec5e9b71e3e07c24432fc1fed39c',
        'file': 'src/wallet/wallet.cpp',
        'func': 'CreateTransaction',
        'add_info': (2632, 2632),
        'del_info': (2573, 2600),
        'up_info': None,
        'down_info': None
    },

    {
        # 22
        # https://github.com/bitcoin/bitcoin/pull/14993
        # rpc: Fix data race (UB) in InterruptRPC()
        # introduce commit
        # https://github.com/practicalswift/bitcoin/commit/ff6a7af154f2151c93a06b7ee86c167603c5ac55
        # time Jul 11, 2014
        'sha': '6c10037f72073eecc674c313580ef50a4f1e1e44',
        'file': 'src/rpc/server.cpp',
        'add_info': (27, 27),
        'del_info': (27, 27),
        'up_info': None,
        'down_info': None
    },

    {
        # 23
        # https://github.com/bitcoin/bitcoin/pull/14897
        # This code makes executing two particular (and potentially other) attacks harder.
        'sha': '1cff3d6cb017aea87d16cbda0768bbab256d16da',
        'file': 'src/net_processing.cpp',
        'func': 'SendMessages',
        'add_info': (3894, 3896),
        'del_info': (3747, 3748),
        'up_info': None,
        'down_info': None
    },

    {
        # 24
        # https://github.com/bitcoin/bitcoin/pull/14728
        # fix uninitialized read when stringifying an addrLocal
        # introduction commit:
        # https://github.com/kazcw/bitcoin/commit/21e5b96ff417f304e624052f629e2b030984180f
        # time: Aug 1, 2016
        'sha': 'b7b36decaf878a8c1dcfdb4a27196c730043474b',
        'file': 'src/netaddress.h',
        'add_info':  (36, 36),
        'del_info': (36, 36),
        'up_info': None,
        'down_info': None
    },

    {
        # 25
        # https://github.com/bitcoin/bitcoin/pull/14073
        # blockfilter: Avoid out-of-bounds script access
        'sha': 'f05599557a8305d16bd5965921583af9d012fc27',
        'file': 'src/blockfilter.cpp',
        'add_info': (211, 211),
        'del_info': (211, 211),
        'up_info': True,
        'down_info': None
    },

    {
        # 26
        # https://github.com/bitcoin/bitcoin/pull/13907
        # Introduce a maximum size for locators
        'sha': 'e254ff5d53b79bee29203b965fca572f218bff54',
        'file': 'src/net_processing.cpp',
        'func': 'processmessage',
        'add_info': (2140, 2145),
        'del_info': None,
        'up_info': None,
        'down_info': True
    },

    {
        # 27
        # https://github.com/bitcoin/bitcoin/pull/13808
        # Issue brought up in https://github.com/bitcoin/bitcoin/pull/12257\#discussion_r204554549
        'sha': '18f690ec2f7eb1b4aa51825bfed0cbfdadc93ac7',
        'file': 'src/wallet/wallet.cpp',
        'func': 'SelectCoins',
        'add_info': (2530, 2535),
        'del_info': None,
        'up_info': True,
        'down_info': None
    },

    {
        # 28
        # https://github.com/bitcoin/bitcoin/pull/13712
        # wallet: Fix non-determinism in ParseHDKeypath(...). Avoid using an uninitialized
        'sha': '27ee53c1aedae4f27458537c61804b6fef34ce3c',
        'file': 'src/wallet/rpcwallet.cpp',
        'func': 'ParseHDKeypath',
        'add_info': (4436, 4438),
        'del_info': (4436, 4436),
        'up_info': None,
        'down_info': None
    },

    {
        # 29
        # https://github.com/bitcoin/bitcoin/pull/13721
        # Fix merging of global unknown data in PSBTs
        'sha': 'fad231ad41e12b7047deb64220942ca8cb8357bc',
        'file': 'src/script/sign.cpp',
        'func': 'merge',
        'add_info': (484, 484),
        'del_info': None,
        'up_info': True,
        'down_info': True
    },

    {
        # 30
        # https://github.com/bitcoin/bitcoin/pull/13683
        # Avoid potential null pointer dereference in CWalletTx::GetAvailableCredit(...).
        # introduction commit:
        # https://github.com/practicalswift/bitcoin/commit/4279da47855ec776f8d57c6579fe89afc9cbe8c1
        # time: Jun 29, 2018
        'sha': 'd06330396f64b9a3a3016afc1f937633b4b322ab',
        'file': 'src/wallet/wallet.cpp',
        'func': 'GetAvailableCredit',
        'add_info': (1950, 1950),
        'del_info': None,
        'up_info': True,
        'down_info': True
    },

    {
        # 31
        # https://github.com/bitcoin/bitcoin/pull/13546
        # Avoid use of uninitialized value bnb_used in CWallet::CreateTransaction(...).
        'sha': 'a23a7f60aa07de52d23ff1f2034fc43926ec3520',
        'file': 'src/wallet/wallet.cpp',
        'add_info': (2847, 2848),
        'del_info': None,
        'up_info': True,
        'down_info': True
    },

]
