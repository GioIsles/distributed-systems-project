# ==========================================
# PART 1: PHYSICAL CLOCKS (NTP Simulation)
# ==========================================
class PhysicalNode:
    def __init__(self, node_id, clock):
        self.node_id = node_id
        self.clock = clock

    def send_request(self, server, send_latency, return_latency):
        t1 = self.clock # T1: Client records time before sending
        
        self.clock += send_latency
        server.clock += send_latency
        
        t2 = server.clock # T2: Server records time request received
        
        # Simulate slight processing time on server
        server_processing_time = 1
        self.clock += server_processing_time
        server.clock += server_processing_time
        
        t3 = server.clock # T3: Server records time response sent
        
        self.clock += return_latency
        server.clock += return_latency
        
        t4 = self.clock # T4: Client records time response received
        
        # ============================
        # NTP CALCULATIONS
        # ============================

        # Round-trip delay
        delta = (t4 - t1) - (t3 - t2)

        # Clock offset
        theta = ((t2 - t1) + (t3 - t4)) / 2

        # Adjust client clock
        self.clock += theta

def run_ntp_simulation(send_latency, return_latency):
    server = PhysicalNode("server", 100)
    client = PhysicalNode("client", 50)

    print(f"\n--- NTP Clocks | Latencies -> Send: {send_latency}, Return: {return_latency} ---")
    client.send_request(server, send_latency, return_latency)
    print(f"After Sync: Server clock: {server.clock}, Client clock: {client.clock}")
    print(f"Final Skew (Server - Client): {server.clock - client.clock}")

# ==========================================
# PART 2: LOGICAL CLOCKS (Lamport)
# ==========================================
class LogicalNode:
    def __init__(self, name):
        self.name = name
        self.clock = 0

    def local_event(self):
        # Lamport Rule: increment on internal event
        self.clock += 1
        print(f"{self.name} local event. Clock is now: {self.clock}")

    def send_message(self, receiver):
        # Lamport Rule: increment before sending
        self.clock += 1
        print(f"{self.name} sends message. Clock is now: {self.clock}")
        return self.clock

    def receive_message(self, sender_name, msg_clock):
        # Lamport Rule: max(local, received) + 1
        self.clock = max(self.clock, msg_clock) + 1
        print(f"{self.name} receives message from {sender_name}. Clock is now: {self.clock}")

def run_logical_simulation():
    print("\n--- Logical Clocks (Lamport Simulation) ---")
    node_a = LogicalNode("A")
    node_b = LogicalNode("B")
    node_c = LogicalNode("C")

    node_a.local_event()
    msg_time = node_a.send_message(node_b)
    node_b.receive_message("A", msg_time)
    node_b.local_event()
    msg_time2 = node_b.send_message(node_c)
    node_c.receive_message("B", msg_time2)

# ==========================================
# RUN SIMULATIONS
# ==========================================
if __name__ == "__main__":
    run_ntp_simulation(5, 5) # Symmetric
    run_ntp_simulation(2, 8) # Asymmetric
    run_logical_simulation()