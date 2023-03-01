from pickhardtpayments.pickhardtpayments import SyncSimulatedPaymentSession, UncertaintyNetwork, OracleLightningNetwork


class IteratedGame:
    def __init__(self,
                payment_session: SyncSimulatedPaymentSession,
                uncertainity_network: UncertaintyNetwork,
                oracle_lightning_network: OracleLightningNetwork,
                payments_to_simulate: int = 10,
                payments_amount: int = 1000,
                mu: int = 10,
                base: int = 1000,
                distribution: str = "normal",
                dist_func: str = "linear"):
        self._payment_session = payment_session
        self._uncertainty_network = uncertainity_network
        self._oracle_lightning_network = oracle_lightning_network
        self._payments_to_simulate = payments_to_simulate,
        self._payments_amount = payments_amount,
        self._mu = mu,
        self._base = base,
        self._distribution = distribution,
        self._dist_func = dist_func


