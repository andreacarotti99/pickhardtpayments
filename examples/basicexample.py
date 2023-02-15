from pickhardtpayments.pickhardtpayments import ChannelGraph
from pickhardtpayments.pickhardtpayments import UncertaintyNetwork
from pickhardtpayments.pickhardtpayments import OracleLightningNetwork
from pickhardtpayments.pickhardtpayments import SyncSimulatedPaymentSession
import numpy as np
def main():
    channel_graph = ChannelGraph("listchannels20220412.json")
    uncertainty_network = UncertaintyNetwork(channel_graph)
    oracle_lightning_network = OracleLightningNetwork(channel_graph)

    # We create a payment session which in this case operates by sending out the onions sequentially
    payment_session = SyncSimulatedPaymentSession(oracle_lightning_network, uncertainty_network, prune_network=False)

    # We need to make sure we forget all learnt information on the Uncertainty Network
    payment_session.forget_information()

    # Initialize a new payment session of more than one payment


    RENE = "03efccf2c383d7bf340da9a3f02e2c23104a0e4fe8ac1a880c8e2dc92fbdacd9df"
    C_OTTO = "027ce055380348d7812d2ae7745701c9f93e70c1adeb2657f053f91df4f2843c71"
    tested_amount = 5_000_000  # sats
    payment_session.pickhardt_pay(RENE, C_OTTO, tested_amount, mu=0, base=0)


    # Print RENE balance
    # Print all the nodes involved in the payment balances
    # Make a new payment
    # print all the nodes involved in the payment balances again




if __name__ == "__main__":
    np.random.seed(1)
    main()
