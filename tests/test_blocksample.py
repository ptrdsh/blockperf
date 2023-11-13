import pytest
from datetime import datetime
from blockperf.config import AppConfig, ConfigError
from blockperf.blocksample import BlockSample
from blockperf.nodelogs import LogEventKind, LogEvent
from blockperf.blocksample import slot_time_of


@pytest.fixture
def sample01():
    return BlockSample(
        [
            LogEvent.from_logline(
                """{"app":[],"at":"2023-09-01T14:14:24.55Z",
                        "data":{
                            "deltaq":{"G":2.472594034e-2},
                            "head":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246",
                            "kind":"SendFetchRequest","length":1,
                            "peer":{
                                "local":{"addr":"192.168.0.137","port":"3001"},
                                "remote":{"addr":"3.11.145.214","port":"3002"}
                            }
                        },"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"17608"}"""
            ),
            LogEvent.from_logline(
                """{"app":[],"at":"2023-09-01T14:14:24.56Z",
                        "data":{
                            "deltaq":{"G":8.211184152e-2},
                            "head":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246",
                            "kind":"SendFetchRequest","length":1,
                            "peer":{
                                "local":{"addr":"192.168.0.137","port":"3001"},
                                "remote":{"addr":"66.45.255.78","port":"6000"}
                            }
                        },"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"19105"}"""
            ),
            LogEvent.from_logline(
                """{"app":[],"at":"2023-09-01T14:14:24.58Z",
                        "data":{
                            "block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246",
                            "blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader",
                            "peer":{
                                "local":{"addr":"192.168.0.137","port":"3001"},
                                "remote":{"addr":"3.216.77.109","port":"3001"}
                            },
                            "slot":102011373
                        },"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"19982"}"""
            ),
            LogEvent.from_logline(
                """{"app":[],"at":"2023-09-01T14:14:24.61Z",
                        "data":{
                            "block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246",
                            "delay":0.613318494,"kind":"CompletedBlockFetch",
                            "peer":{
                                "local":{"addr":"192.168.0.137","port":"3001"},
                                "remote":{"addr":"3.11.145.214","port":"3002"}
                            },
                            "size":89587
                        },"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"17607"}"""
            ),
            LogEvent.from_logline(
                """{"app":[],"at":"2023-09-01T14:14:24.63Z",
                        "data":{
                            "block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246",
                            "blockNo":9233842,
                            "kind":"ChainSyncClientEvent.TraceDownloadedHeader",
                            "peer":{
                                "local":{"addr":"192.168.0.137","port":"3001"},
                                "remote":{"addr":"18.158.165.66","port":"3001"}
                            },
                            "slot":102011373
                        },"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"20525"}"""
            ),
            LogEvent.from_logline(
                """{"app":[],"at":"2023-09-01T14:14:24.67Z",
                        "data":{
                            "chainLengthDelta":1,
                            "kind":"TraceAddBlockEvent.AddedToCurrentChain",
                            "newtip":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246@102011373"
                          },"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainDB"],"pid":"1662080","sev":"Notice","thread":"191"}"""
            ),
        ],
    )


@pytest.fixture
def empty_sample():
    return BlockSample(events=[])


def test_first_trace_header(sample01, empty_sample):
    assert not empty_sample.first_trace_header
    assert sample01.first_trace_header
    assert sample01.first_trace_header.kind == LogEventKind.TRACE_DOWNLOADED_HEADER


def test_first_completed_block(sample01, empty_sample):
    assert not empty_sample.first_completed_block
    assert sample01.first_completed_block
    assert sample01.first_completed_block.kind == LogEventKind.COMPLETED_BLOCK_FETCH


def test_fetch_request_completed_block(sample01, empty_sample):
    assert not empty_sample.fetch_request_completed_block
    assert sample01.fetch_request_completed_block
    assert (
        sample01.fetch_request_completed_block.kind == LogEventKind.SEND_FETCH_REQUEST
    )


def test_block_adopt(sample01, empty_sample):
    assert not empty_sample.block_adopt
    assert sample01.block_adopt.kind == LogEventKind.ADDED_TO_CURRENT_CHAIN


def test_is_complete(sample01, empty_sample):
    assert not empty_sample.is_complete()
    assert sample01.is_complete()


def test_is_sane(sample01, empty_sample):
    assert not empty_sample.is_sane()
    assert sample01.is_sane()


def test_header_remote_addr(sample01, empty_sample):
    assert empty_sample.header_remote_addr == ""
    assert sample01.header_remote_addr == "3.216.77.109"


def test_header_remote_port(sample01, empty_sample):
    assert empty_sample.header_remote_port == ""
    assert sample01.header_remote_port == "3001"


def test_slot_num(sample01, empty_sample):
    assert empty_sample.slot_num == 0
    assert sample01.slot_num == 102011373


def test_slot_time(sample01):
    assert int(sample01.slot_time.timestamp()) == 1693577664


def test_header_delta(sample01, empty_sample):
    assert empty_sample.header_delta == 0
    assert sample01.header_delta == 580


def test_block_num(sample01, empty_sample):
    assert empty_sample.block_num == 0
    assert sample01.block_num == 9233842


def block_hash(sample01, empty_sample):
    assert empty_sample.block_hash == ""
    assert empty_sample.block_hash_short == ""

    assert (
        sample01.block_hash
        == "dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246"
    )
    assert sample01.block_hash_short == "dda846c34c"


def test_block_g(sample01, empty_sample):
    assert empty_sample.block_g == 0.0
    assert sample01.block_g == 0.02472594034


def test_block_size(sample01, empty_sample):
    assert empty_sample.block_size == 0
    assert sample01.block_size == 89587


def test_block_delay(sample01, empty_sample):
    assert empty_sample.block_delay == 0.0
    assert sample01.block_delay == 0.613318494


def test_block_request_delta(sample01, empty_sample):
    assert empty_sample.block_request_delta == 0
    assert sample01.block_request_delta == -30


def test_block_response_delta(sample01, empty_sample):
    assert empty_sample.block_response_delta == 0
    assert sample01.block_response_delta == 60


def test_block_adopt_delta(sample01, empty_sample):
    assert empty_sample.block_adopt_delta == 0
    assert sample01.block_adopt_delta == 60


def test_block_remote_addr(sample01, empty_sample):
    assert empty_sample.block_remote_addr == ""
    assert sample01.block_remote_addr == "3.11.145.214"


def test_block_remote_port(sample01, empty_sample):
    assert empty_sample.block_remote_port == ""
    assert sample01.block_remote_port == "3002"


def test_block_local_address(sample01, empty_sample):
    assert empty_sample.block_local_address == ""
    assert sample01.block_local_address == "192.168.0.137"


def test_block_local_port(sample01, empty_sample):
    assert empty_sample.block_local_port == ""
    assert sample01.block_local_port == "3001"


def test_slot_fime_of():
    """Took Slot and time from this Block: https://cardanoscan.io/block/9121756"""
    slot_time = slot_time_of(99692109, "mainnet")
    assert int(slot_time.timestamp()) == 1691258400


"""
{"app":[],"at":"2023-09-01T14:14:24.55Z","data":{"kind":"AcknowledgedFetchRequest","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.11.145.214","port":"3002"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"17608"}
{"app":[],"at":"2023-09-01T14:14:24.55Z","data":{"deltaq":{"G":2.472594034e-2},"head":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","kind":"SendFetchRequest","length":1,"peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.11.145.214","port":"3002"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"17608"}
{"app":[],"at":"2023-09-01T14:14:24.55Z","data":{"kind":"PeersFetch","peers":[{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"35.72.88.112","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.138.253.119","port":"1338"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"107.23.61.45","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"62.171.132.72","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.216.77.109","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"209.250.239.195","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.109.88.104","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.222.59.152","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"13.51.62.37","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.158.165.66","port":"3001"}}},{"declined":"FetchDeclineInFlightThisPeer","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.11.145.214","port":"3002"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.170.158.171","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"81.173.113.182","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"159.69.15.8","port":"3005"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"23.88.127.17","port":"5001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"202.61.245.122","port":"55001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"135.125.145.15","port":"6000"}}},{"kind":"FetchDecision results","length":"1","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.215.7.178","port":"3001"}}}]},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchDecision"],"pid":"1662080","sev":"Info","thread":"201"}
{"app":[],"at":"2023-09-01T14:14:24.55Z","data":{"kind":"AddedFetchRequest","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.215.7.178","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"201"}
{"app":[],"at":"2023-09-01T14:14:24.55Z","data":{"kind":"AcknowledgedFetchRequest","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.215.7.178","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"485"}
{"app":[],"at":"2023-09-01T14:14:24.55Z","data":{"deltaq":{"G":0.10745705309},"head":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","kind":"SendFetchRequest","length":1,"peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.215.7.178","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"485"}
{"app":[],"at":"2023-09-01T14:14:24.56Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"19113"}
{"app":[],"at":"2023-09-01T14:14:24.56Z","data":{"kind":"AddedFetchRequest","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"201"}
{"app":[],"at":"2023-09-01T14:14:24.56Z","data":{"kind":"AcknowledgedFetchRequest","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"19105"}
{"app":[],"at":"2023-09-01T14:14:24.56Z","data":{"deltaq":{"G":8.211184152e-2},"head":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","kind":"SendFetchRequest","length":1,"peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"19105"}
{"app":[],"at":"2023-09-01T14:14:24.57Z","data":{"kind":"StartedFetchBatch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.11.145.214","port":"3002"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"17607"}
{"app":[],"at":"2023-09-01T14:14:24.58Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.216.77.109","port":"3001"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"19982"}
{"app":[],"at":"2023-09-01T14:14:24.58Z","data":{"kind":"AddedFetchRequest","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.216.77.109","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"201"}
{"app":[],"at":"2023-09-01T14:14:24.58Z","data":{"kind":"AcknowledgedFetchRequest","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.216.77.109","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"19978"}
{"app":[],"at":"2023-09-01T14:14:24.58Z","data":{"deltaq":{"G":0.159185334336},"head":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","kind":"SendFetchRequest","length":1,"peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.216.77.109","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"19978"}
{"app":[],"at":"2023-09-01T14:14:24.59Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"107.23.61.45","port":"3001"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"21308"}
{"app":[],"at":"2023-09-01T14:14:24.60Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.222.59.152","port":"3001"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"504"}
{"app":[],"at":"2023-09-01T14:14:24.61Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","delay":0.613318494,"kind":"CompletedBlockFetch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.11.145.214","port":"3002"}},"size":89587},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"17607"}
{"app":[],"at":"2023-09-01T14:14:24.61Z","data":{"kind":"CompletedFetchBatch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.11.145.214","port":"3002"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"17607"}
{"app":[],"at":"2023-09-01T14:14:24.61Z","data":{"kind":"LogValue","name":"before next, messages elided","value":{"contents":3,"tag":"PureI"}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchDecision"],"pid":"1662080","sev":"Info","thread":"201"}
{"app":[],"at":"2023-09-01T14:14:24.61Z","data":{"kind":"PeersFetch","peers":[{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"35.72.88.112","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.138.253.119","port":"1338"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"62.171.132.72","port":"3001"}}},{"declined":"FetchDeclineInFlightThisPeer","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.216.77.109","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"209.250.239.195","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.109.88.104","port":"3001"}}},{"declined":"FetchDeclineInFlightThisPeer","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.215.7.178","port":"3001"}}},{"declined":"FetchDeclineInFlightThisPeer","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"13.51.62.37","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.158.165.66","port":"3001"}}},{"declined":"FetchDeclineInFlightThisPeer","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.11.145.214","port":"3002"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.170.158.171","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"81.173.113.182","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"159.69.15.8","port":"3005"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"23.88.127.17","port":"5001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"202.61.245.122","port":"55001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"135.125.145.15","port":"6000"}}},{"declined":"FetchDeclineConcurrencyLimit FetchModeDeadline 4","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"107.23.61.45","port":"3001"}}},{"declined":"FetchDeclineConcurrencyLimit FetchModeDeadline 4","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.222.59.152","port":"3001"}}}]},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchDecision"],"pid":"1662080","sev":"Info","thread":"201"}
{"app":[],"at":"2023-09-01T14:14:24.63Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.158.165.66","port":"3001"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"20525"}
{"app":[],"at":"2023-09-01T14:14:24.63Z","data":{"block":"fa927c7195b1ffbd5a231cf7bbb8f34af0ed77d0d089a892f5f8ffa79a3c090b","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.138.253.119","port":"1338"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"20691"}
{"app":[],"at":"2023-09-01T14:14:24.63Z","data":{"kind":"PeersFetch","peers":[{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"35.72.88.112","port":"6000"}}},{"declined":"FetchDeclineAlreadyFetched","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"107.23.61.45","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"62.171.132.72","port":"3001"}}},{"declined":"FetchDeclineAlreadyFetched","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.216.77.109","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"209.250.239.195","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.109.88.104","port":"3001"}}},{"declined":"FetchDeclineAlreadyFetched","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.222.59.152","port":"3001"}}},{"declined":"FetchDeclineAlreadyFetched","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.215.7.178","port":"3001"}}},{"declined":"FetchDeclineAlreadyFetched","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"13.51.62.37","port":"3001"}}},{"declined":"FetchDeclineAlreadyFetched","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.158.165.66","port":"3001"}}},{"declined":"FetchDeclineAlreadyFetched","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.11.145.214","port":"3002"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.170.158.171","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"81.173.113.182","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"159.69.15.8","port":"3005"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"23.88.127.17","port":"5001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"202.61.245.122","port":"55001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"135.125.145.15","port":"6000"}}},{"kind":"FetchDecision results","length":"1","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.138.253.119","port":"1338"}}}]},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchDecision"],"pid":"1662080","sev":"Info","thread":"201"}
{"app":[],"at":"2023-09-01T14:14:24.63Z","data":{"kind":"AcknowledgedFetchRequest","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.138.253.119","port":"1338"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"20686"}
{"app":[],"at":"2023-09-01T14:14:24.63Z","data":{"deltaq":{"G":0.231829240052},"head":"fa927c7195b1ffbd5a231cf7bbb8f34af0ed77d0d089a892f5f8ffa79a3c090b","kind":"SendFetchRequest","length":1,"peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.138.253.119","port":"1338"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"20686"}
{"app":[],"at":"2023-09-01T14:14:24.63Z","data":{"kind":"AddedFetchRequest","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.138.253.119","port":"1338"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"201"}
{"app":[],"at":"2023-09-01T14:14:24.63Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"159.69.15.8","port":"3005"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"17883"}
{"app":[],"at":"2023-09-01T14:14:24.64Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"23.88.127.17","port":"5001"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"21128"}
{"app":[],"at":"2023-09-01T14:14:24.64Z","data":{"kind":"StartedFetchBatch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.215.7.178","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"484"}
{"app":[],"at":"2023-09-01T14:14:24.65Z","data":{"kind":"StartedFetchBatch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"19104"}
{"app":[],"at":"2023-09-01T14:14:24.65Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"15187"}
{"app":[],"at":"2023-09-01T14:14:24.65Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"202.61.245.122","port":"55001"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"941"}
{"app":[],"at":"2023-09-01T14:14:24.67Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"209.250.239.195","port":"6000"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"9497"}
{"app":[],"at":"2023-09-01T14:14:24.67Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246@102011373","kind":"TraceAddBlockEvent.AddBlockValidation.ValidCandidate"},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainDB"],"pid":"1662080","sev":"Info","thread":"191"}
{"app":[],"at":"2023-09-01T14:14:24.67Z","data":{"chainLengthDelta":1,"kind":"TraceAddBlockEvent.AddedToCurrentChain","newtip":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246@102011373"},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainDB"],"pid":"1662080","sev":"Notice","thread":"191"}
{"app":[],"at":"2023-09-01T14:14:24.68Z","data":{"kind":"StartedFetchBatch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.216.77.109","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"19977"}
{"app":[],"at":"2023-09-01T14:14:24.68Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"81.173.113.182","port":"6000"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"15354"}
{"app":[],"at":"2023-09-01T14:14:24.69Z","data":{"kind":"TraceMempoolRemoveTxs","mempoolSize":{"bytes":5130,"numTxs":5},"txs":[{"txid":"c635a305"},{"txid":"cc02f792"},{"txid":"ba791a19"},{"txid":"6055c31c"},{"txid":"353b129c"},{"txid":"9879c2dd"},{"txid":"a3cd512b"},{"txid":"f9e8218d"},{"txid":"7185b869"},{"txid":"ebebdba4"},{"txid":"68c2dad3"},{"txid":"989c98d5"},{"txid":"a9682d2a"},{"txid":"18dc6a98"},{"txid":"bf6032f0"},{"txid":"bb19d980"},{"txid":"c0dddc5d"},{"txid":"1100d744"},{"txid":"6dcba7fa"},{"txid":"00057207"},{"txid":"b875d204"},{"txid":"4c7e4931"},{"txid":"f9bd3f40"},{"txid":"13f4db3e"},{"txid":"0bee18bf"},{"txid":"f3517307"},{"txid":"36365963"},{"txid":"6a0c940e"},{"txid":"6eba3ff4"},{"txid":"25fb5023"},{"txid":"fa79642c"},{"txid":"41a2b559"},{"txid":"3293f18d"},{"txid":"5dcdfcbe"},{"txid":"7c1b484c"},{"txid":"22ca05e4"},{"txid":"92c64111"},{"txid":"0a0b39a9"},{"txid":"3e0720e4"},{"txid":"b4b5c5e6"},{"txid":"9a24df96"}]},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.Mempool"],"pid":"1662080","sev":"Info","thread":"199"}
{"app":[],"at":"2023-09-01T14:14:24.69Z","data":{"block":"fa927c7195b1ffbd5a231cf7bbb8f34af0ed77d0d089a892f5f8ffa79a3c090b","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.109.88.104","port":"3001"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"518"}
{"app":[],"at":"2023-09-01T14:14:24.70Z","data":{"kind":"PeersFetch","peers":[{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"35.72.88.112","port":"6000"}}},{"declined":"FetchDeclineInFlightThisPeer","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.138.253.119","port":"1338"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"107.23.61.45","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"62.171.132.72","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.216.77.109","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"209.250.239.195","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.222.59.152","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.215.7.178","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"13.51.62.37","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.158.165.66","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.11.145.214","port":"3002"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.170.158.171","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"81.173.113.182","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"159.69.15.8","port":"3005"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"23.88.127.17","port":"5001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"202.61.245.122","port":"55001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"135.125.145.15","port":"6000"}}},{"declined":"FetchDeclineConcurrencyLimit FetchModeDeadline 4","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.109.88.104","port":"3001"}}}]},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchDecision"],"pid":"1662080","sev":"Info","thread":"201"}
{"app":[],"at":"2023-09-01T14:14:24.72Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","delay":0.725346074,"kind":"CompletedBlockFetch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.216.77.109","port":"3001"}},"size":89587},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"19977"}
{"app":[],"at":"2023-09-01T14:14:24.72Z","data":{"kind":"CompletedFetchBatch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.216.77.109","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"19977"}
{"app":[],"at":"2023-09-01T14:14:24.72Z","data":{"kind":"PeersFetch","peers":[{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"35.72.88.112","port":"6000"}}},{"declined":"FetchDeclineInFlightThisPeer","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.138.253.119","port":"1338"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"107.23.61.45","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"62.171.132.72","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.216.77.109","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"209.250.239.195","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.222.59.152","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.215.7.178","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"13.51.62.37","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.158.165.66","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.11.145.214","port":"3002"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.170.158.171","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"81.173.113.182","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"159.69.15.8","port":"3005"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"23.88.127.17","port":"5001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"202.61.245.122","port":"55001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"135.125.145.15","port":"6000"}}},{"kind":"FetchDecision results","length":"1","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.109.88.104","port":"3001"}}}]},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchDecision"],"pid":"1662080","sev":"Info","thread":"201"}
{"app":[],"at":"2023-09-01T14:14:24.72Z","data":{"kind":"AddedFetchRequest","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.109.88.104","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"201"}
{"app":[],"at":"2023-09-01T14:14:24.72Z","data":{"kind":"AcknowledgedFetchRequest","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.109.88.104","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"513"}
{"app":[],"at":"2023-09-01T14:14:24.72Z","data":{"deltaq":{"G":0.134593002578},"head":"fa927c7195b1ffbd5a231cf7bbb8f34af0ed77d0d089a892f5f8ffa79a3c090b","kind":"SendFetchRequest","length":1,"peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.109.88.104","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"513"}
{"app":[],"at":"2023-09-01T14:14:24.73Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.170.158.171","port":"3001"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"471"}
{"app":[],"at":"2023-09-01T14:14:24.74Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"135.125.145.15","port":"6000"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"899"}
{"app":[],"at":"2023-09-01T14:14:24.74Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"62.171.132.72","port":"3001"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"21132"}
{"app":[],"at":"2023-09-01T14:14:24.75Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"13.51.62.37","port":"3001"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"21143"}
{"app":[],"at":"2023-09-01T14:14:24.79Z","data":{"kind":"StartedFetchBatch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.138.253.119","port":"1338"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"20685"}
{"app":[],"at":"2023-09-01T14:14:24.81Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","delay":0.815161905,"kind":"CompletedBlockFetch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}},"size":89587},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"19104"}
{"app":[],"at":"2023-09-01T14:14:24.81Z","data":{"kind":"CompletedFetchBatch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"19104"}
{"app":[],"at":"2023-09-01T14:14:24.83Z","data":{"block":"dda846c34c0f219c26ded0994ef0beace1dea54487d60e0b4afe5f6f4fe3d246","delay":0.832114369,"kind":"CompletedBlockFetch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.215.7.178","port":"3001"}},"size":89587},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"484"}
{"app":[],"at":"2023-09-01T14:14:24.83Z","data":{"kind":"CompletedFetchBatch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.215.7.178","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"484"}
{"app":[],"at":"2023-09-01T14:14:24.84Z","data":{"kind":"StartedFetchBatch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.109.88.104","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"512"}
{"app":[],"at":"2023-09-01T14:14:24.92Z","data":{"kind":"ChainSyncClientEvent.TraceRolledBack","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}},"tip":{"headerHash":"ae06d3a31a7dbb3af577ed0271723fc24cd17ef6e3e9be58b7631b1ac3ebc1e0","kind":"BlockPoint","slot":102011319}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Notice","thread":"15187"}
{"app":[],"at":"2023-09-01T14:14:24.93Z","data":{"block":"fa927c7195b1ffbd5a231cf7bbb8f34af0ed77d0d089a892f5f8ffa79a3c090b","blockNo":9233842,"kind":"ChainSyncClientEvent.TraceDownloadedHeader","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}},"slot":102011373},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Info","thread":"15187"}
{"app":[],"at":"2023-09-01T14:14:24.93Z","data":{"kind":"PeersFetch","peers":[{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"35.72.88.112","port":"6000"}}},{"declined":"FetchDeclineInFlightThisPeer","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.138.253.119","port":"1338"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"107.23.61.45","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"62.171.132.72","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.216.77.109","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"209.250.239.195","port":"6000"}}},{"declined":"FetchDeclineInFlightThisPeer","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.109.88.104","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.222.59.152","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.215.7.178","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"13.51.62.37","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.158.165.66","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.11.145.214","port":"3002"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.170.158.171","port":"3001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"81.173.113.182","port":"6000"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"159.69.15.8","port":"3005"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"23.88.127.17","port":"5001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"202.61.245.122","port":"55001"}}},{"declined":"FetchDeclineChainNotPlausible","kind":"FetchDecision declined","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"135.125.145.15","port":"6000"}}},{"kind":"FetchDecision results","length":"1","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}}}]},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchDecision"],"pid":"1662080","sev":"Info","thread":"201"}
{"app":[],"at":"2023-09-01T14:14:24.93Z","data":{"kind":"AddedFetchRequest","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"201"}
{"app":[],"at":"2023-09-01T14:14:24.93Z","data":{"kind":"AcknowledgedFetchRequest","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"15182"}
{"app":[],"at":"2023-09-01T14:14:24.93Z","data":{"deltaq":{"G":5.584729666e-3},"head":"fa927c7195b1ffbd5a231cf7bbb8f34af0ed77d0d089a892f5f8ffa79a3c090b","kind":"SendFetchRequest","length":1,"peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"15182"}
{"app":[],"at":"2023-09-01T14:14:24.93Z","data":{"kind":"StartedFetchBatch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"15181"}
{"app":[],"at":"2023-09-01T14:14:24.95Z","data":{"block":"fa927c7195b1ffbd5a231cf7bbb8f34af0ed77d0d089a892f5f8ffa79a3c090b","delay":0.952392272,"kind":"CompletedBlockFetch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}},"size":89587},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"15181"}
{"app":[],"at":"2023-09-01T14:14:24.95Z","data":{"block":{"hash":"fa927c7195b1ffbd5a231cf7bbb8f34af0ed77d0d089a892f5f8ffa79a3c090b","kind":"Point","slot":102011373},"kind":"TraceAddBlockEvent.TrySwitchToAFork"},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainDB"],"pid":"1662080","sev":"Info","thread":"191"}
{"app":[],"at":"2023-09-01T14:14:24.95Z","data":{"kind":"CompletedFetchBatch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"5.45.109.162","port":"5250"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"15181"}
{"app":[],"at":"2023-09-01T14:14:24.97Z","data":{"kind":"TraceMempoolAddedTx","mempoolSize":{"bytes":6069,"numTxs":6},"tx":{"txid":"3713b02b"}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.Mempool"],"pid":"1662080","sev":"Info","thread":"19409"}
{"app":[],"at":"2023-09-01T14:14:25.01Z","data":{"chainLengthDelta":0,"kind":"TraceAddBlockEvent.SwitchedToAFork","newtip":"fa927c7195b1ffbd5a231cf7bbb8f34af0ed77d0d089a892f5f8ffa79a3c090b@102011373","realFork":true},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainDB"],"pid":"1662080","sev":"Notice","thread":"191"}
{"app":[],"at":"2023-09-01T14:14:25.09Z","data":{"kind":"ChainSyncClientEvent.TraceRolledBack","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"66.45.255.78","port":"6000"}},"tip":{"headerHash":"ae06d3a31a7dbb3af577ed0271723fc24cd17ef6e3e9be58b7631b1ac3ebc1e0","kind":"BlockPoint","slot":102011319}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Notice","thread":"19113"}
{"app":[],"at":"2023-09-01T14:14:25.09Z","data":{"block":"fa927c7195b1ffbd5a231cf7bbb8f34af0ed77d0d089a892f5f8ffa79a3c090b","delay":1.092654207,"kind":"CompletedBlockFetch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.109.88.104","port":"3001"}},"size":89587},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"512"}
{"app":[],"at":"2023-09-01T14:14:25.09Z","data":{"kind":"CompletedFetchBatch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"3.109.88.104","port":"3001"}}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"512"}
{"app":[],"at":"2023-09-01T14:14:25.10Z","data":{"kind":"ChainSyncClientEvent.TraceRolledBack","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"209.250.239.195","port":"6000"}},"tip":{"headerHash":"ae06d3a31a7dbb3af577ed0271723fc24cd17ef6e3e9be58b7631b1ac3ebc1e0","kind":"BlockPoint","slot":102011319}},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.ChainSyncClient"],"pid":"1662080","sev":"Notice","thread":"9497"}
{"app":[],"at":"2023-09-01T14:14:25.10Z","data":{"block":"fa927c7195b1ffbd5a231cf7bbb8f34af0ed77d0d089a892f5f8ffa79a3c090b","delay":1.105331477,"kind":"CompletedBlockFetch","peer":{"local":{"addr":"192.168.0.137","port":"3001"},"remote":{"addr":"18.138.253.119","port":"1338"}},"size":89587},"env":"8.1.1:ea2c0","host":"mainnetf","loc":null,"msg":"","ns":["cardano.node.BlockFetchClient"],"pid":"1662080","sev":"Info","thread":"20685"}
"""
