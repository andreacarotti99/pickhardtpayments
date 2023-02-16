from pickhardtpayments.pickhardtpayments import ChannelGraph
from pickhardtpayments.pickhardtpayments import UncertaintyNetwork
from pickhardtpayments.pickhardtpayments import OracleLightningNetwork
from pickhardtpayments.pickhardtpayments import SyncSimulatedPaymentSession
import numpy as np

DEFAULT_BASE_THRESHOLD = 0

def run_success_payments_simulation(payment_session, uncertainity_network, payments_to_simulate, payments_amount, mu, base):
        paymentNumber = 0
        senders_fee = {}
        payments_fees = []
        payment_session.forget_information()
        while paymentNumber < payments_to_simulate:
            print("==============================================================================")
            print("Payment: " + str((paymentNumber + 1)) + "  ==================================================================")
            src = uncertainity_network.get_random_node()
            dst = uncertainity_network.get_random_node()
            while dst == src:
                dst = uncertainity_network.get_random_node()
            print("Source: " + str(src) + "\nDestination: " + str(dst))
            # perform the payment
            payment = payment_session.pickhardt_pay(src, dst, payments_amount, mu, base)
            if payment.successful:
                paymentNumber += 1
                payments_fees.append(payment.fee_per_node)


def main():
    channel_graph = ChannelGraph("listchannels20220412.json")
    uncertainty_network = UncertaintyNetwork(channel_graph)
    oracle_lightning_network = OracleLightningNetwork(channel_graph)
    payment_session = SyncSimulatedPaymentSession(oracle_lightning_network, uncertainty_network, prune_network=False)
    payment_session.forget_information()

    RENE = "03efccf2c383d7bf340da9a3f02e2c23104a0e4fe8ac1a880c8e2dc92fbdacd9df"
    C_OTTO = "027ce055380348d7812d2ae7745701c9f93e70c1adeb2657f053f91df4f2843c71"
    NODE_1_HOP_TO_OTTO = "02d4b432058ec31e38f6f35d22a487b7db04c4bf70f201f601b66f7b4358242b03"
    NODE_2_HOP_TO_OTTO = "02c1321de5a127023115b90f33ae1244349269f5d18d3ea4014be697e700c07ccc"

    # print(oracle_lightning_network.network.get_edge_data(RENE, NODE_1_HOP_TO_OTTO, '624881x1940x0')['channel'].actual_liquidity)

    A = "03ea257b4bfbc1fde63be9deedadad8032fbfb082c35327f55d77ee89ab2cd3a89"
    B = "0344ae9dbca74941379d84594af16b6895c77257a12e6bcd62b23a5c665569809f"
    tested_amount = 1000  # sats
    mu = 0
    base = 10_000_000

    p1 = payment_session.pickhardt_pay(A, B, tested_amount, mu=0, base=0)
    # p2 = payment_session.pickhardt_pay(RENE, C_OTTO, tested_amount, mu=0, base=0)

    # print(p.fee_per_node)
    # print(oracle_lightning_network.network.get_edge_data(RENE, NODE_1_HOP_TO_OTTO, '624881x1940x0')['channel'].actual_liquidity)

    payments_to_simulate = 5
    payments_amount = 1000


    # run_success_payments_simulation(payment_session, uncertainty_network, payments_to_simulate, payments_amount, mu, base)




if __name__ == "__main__":
    np.random.seed(1)
    main()
