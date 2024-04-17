// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.21;

import {Script, console2} from "forge-std/Script.sol";
import {OffchainResolver} from "src/OffchainResolver.sol";

contract DeployOffchainReslover is Script {

    uint256 privatekey;
    address[] signers;

    function setUp() public {
        privatekey = vm.envUint("DEPLOYER_PRIVATE_KEY");
        signers.push(vm.envAddress("DEPLOYER_ADDRESS"));
        
    }

    function run() public {
        vm.broadcast(privatekey);

        OffchainResolver reslover = new OffchainResolver("https://extranonce.ddnsfree.com:8000/gateway/{sender}.json", signers);
        console2.log("OffchainResolver %s", address(reslover));
        
    }
    
}
