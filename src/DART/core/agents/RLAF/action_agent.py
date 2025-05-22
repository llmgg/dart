from ...base.agent import Agent


class ActionAgent(Agent):
    def set_action_policy(self, **kwargs):
        raise NotImplementedError()

    def set_reaction_policy(self, **kwargs):
        raise NotImplementedError()

