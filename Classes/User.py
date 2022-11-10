class User:
    def __init__(self, name=None):
        self.name = name
        self.budget_id = None
    
    def set_budget_reference(self, budget_id):
        self.budget_id = budget_id