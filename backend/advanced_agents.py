import time
from datetime import datetime

class BaseAgent:
    def __init__(self, name):
        self.name = name

    def log(self, message):
        return {
            'agent': self.name,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__('PlannerAgent')

    def create_high_level_plan(self, prompt):
        logs = []
        logs.append(self.log('Analyzing high-level requirements'))
        time.sleep(0.5)
        logs.append(self.log('Defining modules, interfaces, and data flow'))
        time.sleep(0.5)
        plan = {
            'project_overview': f'High level plan based on: {prompt[:120]}',
            'modules': ['data_ingest', 'data_processing', 'model', 'api', 'docs']
        }
        logs.append(self.log('Plan created'))
        return {'plan': plan, 'logs': logs}

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__('ResearchAgent')

    def gather_requirements(self, plan):
        logs = []
        logs.append(self.log('Researching libraries, data sources and best practices'))
        time.sleep(0.4)
        logs.append(self.log('Collected potential datasets and tool choices'))
        return {'research': {'datasets': ['dataset_a', 'dataset_b'], 'libraries': ['pandas','scikit-learn']}, 'logs': logs}

class DataEngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__('DataEngineerAgent')

    def design_pipeline(self, research):
        logs = []
        logs.append(self.log('Designing ETL pipeline and storage schema'))
        time.sleep(0.4)
        logs.append(self.log('Defined data ingestion, cleaning and transformation steps'))
        pipeline_spec = {'etl': ['ingest', 'clean', 'transform'], 'storage': 'postgresql'}
        return {'pipeline': pipeline_spec, 'logs': logs}

class MLEngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__('MLEngineerAgent')

    def design_model(self, pipeline):
        logs = []
        logs.append(self.log('Selecting model architectures and evaluation metrics'))
        time.sleep(0.4)
        logs.append(self.log('Prepared MLOps integration plan'))
        model_spec = {'model_type': 'classification', 'framework': 'scikit-learn'}
        return {'model': model_spec, 'logs': logs}

class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__('ReviewerAgent')

    def review(self, artifacts):
        logs = []
        logs.append(self.log('Reviewing generated architecture and specs'))
        time.sleep(0.3)
        logs.append(self.log('Found minor improvements, suggested updates'))
        return {'review': {'issues': [], 'suggestions': ['improve docs']}, 'logs': logs}

class DocumentationAgent(BaseAgent):
    def __init__(self):
        super().__init__('DocumentationAgent')

    def generate_docs(self, plan, research, pipeline, model):
        logs = []
        logs.append(self.log('Generating high-level documentation and README'))
        time.sleep(0.3)
        docs = {'README.md': '# Project Overview\n\nGenerated high-level documentation.'}
        logs.append(self.log('Documentation created'))
        return {'docs': docs, 'logs': logs}
