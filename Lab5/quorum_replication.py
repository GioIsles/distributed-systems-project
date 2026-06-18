import time
import random
from collections import Counter


class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.store = {}
        self.available = True

    def simulate_latency(self):
        time.sleep(random.uniform(0.05, 0.15))

    def write(self, key, value):
        self.simulate_latency()
        self.store[key] = value

    def read(self, key):
        self.simulate_latency()
        return self.store.get(key, None)


class QuorumCluster:
    def __init__(self, n=3):
        self.nodes = [Node(i) for i in range(n)]

    def reset_nodes(self):
        for node in self.nodes:
            node.available = True

    def write(self, key, value, write_quorum):
        start = time.perf_counter()

        acknowledgements = 0

        for node in self.nodes:

            if not node.available:
                continue

            node.write(key, value)
            acknowledgements += 1

            if acknowledgements >= write_quorum:
                latency = (
                    time.perf_counter() - start
                ) * 1000

                return True, latency

        latency = (
            time.perf_counter() - start
        ) * 1000

        return False, latency

    def read(self, key, read_quorum):
        start = time.perf_counter()

        responses = []

        for node in self.nodes:

            if not node.available:
                continue

            value = node.read(key)

            if value is not None:
                responses.append(value)

            if len(responses) >= read_quorum:
                break

        latency = (
            time.perf_counter() - start
        ) * 1000

        if len(responses) < read_quorum:
            return None, False, latency

        most_common = Counter(
            responses
        ).most_common(1)[0][0]

        return most_common, True, latency


def run_scenario(name, R, W):
    print("\n" + "=" * 60)
    print(f"SCENARIO {name}")
    print(f"R = {R}, W = {W}")
    print("=" * 60)

    cluster = QuorumCluster(3)

    successful_reads = 0
    failed_reads = 0
    successful_writes = 0
    failed_writes = 0

    read_latencies = []
    write_latencies = []

    for i in range(5):

        success, latency = cluster.write(
            "account",
            f"value_{i}",
            W
        )

        write_latencies.append(latency)

        if success:
            successful_writes += 1
        else:
            failed_writes += 1

        value, success, latency = cluster.read(
            "account",
            R
        )

        read_latencies.append(latency)

        if success:
            successful_reads += 1
        else:
            failed_reads += 1

    avg_write = sum(write_latencies) / len(write_latencies)
    avg_read = sum(read_latencies) / len(read_latencies)

    print("\nResults")
    print(f"Average Write Latency: {avg_write:.2f} ms")
    print(f"Average Read Latency:  {avg_read:.2f} ms")

    print(f"\nSuccessful Writes: {successful_writes}")
    print(f"Failed Writes:     {failed_writes}")

    print(f"Successful Reads:  {successful_reads}")
    print(f"Failed Reads:      {failed_reads}")

    return avg_write, avg_read


def demonstrate_stale_read():
    print("\n" + "=" * 60)
    print("STALE READ DEMONSTRATION")
    print("Scenario C: R=1, W=1")
    print("=" * 60)

    cluster = QuorumCluster(3)

    cluster.write("balance", "OLD", 3)

    print("\nInitial value written: OLD")

    cluster.nodes[1].available = False

    print("Node 1 taken offline")

    cluster.write("balance", "NEW", 1)

    print("NEW value written using W=1")

    cluster.nodes[1].available = True

    print("Node 1 restored")

    stale_value = cluster.nodes[1].read("balance")

    print(f"\nReading from restored node:")
    print(f"Returned value: {stale_value}")

    if stale_value == "OLD":
        print(
            "STALE READ OBSERVED "
            "(expected under eventual consistency)"
        )
    else:
        print("No stale read observed")


def main():
    print("\nQUORUM-BASED REPLICATION SIMULATION")

    results = []

    results.append(
        ("A", 2, 2, *run_scenario("A", 2, 2))
    )

    results.append(
        ("B", 3, 1, *run_scenario("B", 3, 1))
    )

    results.append(
        ("C", 1, 1, *run_scenario("C", 1, 1))
    )

    demonstrate_stale_read()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(
        f"{'Scenario':<10}"
        f"{'R':<5}"
        f"{'W':<5}"
        f"{'Write(ms)':<15}"
        f"{'Read(ms)':<15}"
    )

    for row in results:
        scenario, r, w, write_lat, read_lat = row

        print(
            f"{scenario:<10}"
            f"{r:<5}"
            f"{w:<5}"
            f"{write_lat:<15.2f}"
            f"{read_lat:<15.2f}"
        )


if __name__ == "__main__":
    main()