from ...base.agent import Agent


class RewardAgent(Agent):
    def set_reward_policy(self, **kwargs):
        raise NotImplementedError()
