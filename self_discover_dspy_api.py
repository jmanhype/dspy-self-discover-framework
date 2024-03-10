from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import dspy
from pathlib import Path
import json
from groq import Groq as GroqClient  # Ensure this matches your actual Groq client import
from dsp import LM
import os
from interpreter import interpreter as oi
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

class ReasoningStep(BaseModel):
    step_description: str = Field(..., description="Description of the reasoning step")
    action: str = Field(..., description="The action to be taken in this step")
    inputs: Optional[List[str]] = Field(None, description="Optional inputs needed for the action")

class ReasoningStructure(BaseModel):
    task_description: str = Field(..., description="Description of the task to be solved")
    steps: List[ReasoningStep] = Field(..., description="List of steps involved in reasoning")

class ReasoningOutput(BaseModel):
    implemented_reasoning_structures: ReasoningStructure = Field(..., description="Implemented reasoning structures to solve the task")


class TaskRequest(BaseModel):
    description: str
    task_type: str  # Newly added attribute

class GenerateCodeModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.translator = TranslateToCode()

    def translate_to_code(self, reasoning_structure: ReasoningStructure) -> str:
        code_snippets = [self.translator.translate_step(step) for step in reasoning_structure.steps]
        return "\n".join(code_snippets)
    
    def forward(self, reasoning_structure: ReasoningStructure) -> str:
        generated_code = self.translate_to_code(reasoning_structure)
        execution_result = interpreter.chat(f"```python\n{generated_code}\n```", display=False)
        return execution_result

class TranslateToCode:
    def __init__(self):
        self.patterns = {
            "calculate": "result = {expression}",
            "compare": "if {condition}:",
            # Extend this dictionary with more actions and corresponding code templates
        }

    def translate_step(self, step: ReasoningStep) -> str:
        template = self.patterns.get(step.action, "# TODO: Implement logic for '{step.action}'")
        return template.format(expression=step.step_description, condition=step.step_description)
        # Adjust the format call as necessary based on the expected details in step_description




class Groq(LM):
    def __init__(self, model="mixtral-8x7b-32768", **kwargs):
        super().__init__(model)
        self.model = model  # Explicitly set the model attribute
        self.client = GroqClient(api_key=os.environ.get("GROQ_API_KEY"))

    # Implement the basic_request method
    def basic_request(self, prompt, **kwargs):
        # Dummy implementation
        pass

    def __call__(self, prompt, only_completed=True, return_sorted=False, **kwargs):
        chat_completion = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=kwargs.get("model", self.model),
        )
        assert chat_completion.choices and chat_completion.choices[0].message.content, "API response is empty or null."
        return [chat_completion.choices[0].message.content]


class CodeExecutionRequest(BaseModel):
    code: str

class TaskRequest(BaseModel):
    description: str
    # Additional fields as necessary

app = FastAPI()

# Global variable for Groq model
groq_model = None

def configure_dspy():
    global groq_model
    groq_model = Groq(model="mixtral-8x7b-32768")
    dspy.settings.configure(lm=groq_model)

# Load and prepare reasoning modules
def load_and_prepare_reasoning_modules():
    cwd = Path.cwd()
    fp_reasoning_modules_json = cwd / "./reasoning_modules.json"
    with open(fp_reasoning_modules_json, "r") as file:
        data = json.load(file)
    reasoning_modules = data.get("reasoning_modules", [])
    reasoning_modules_text = ", ".join([f'({module["type"]}: {module["description"]})' for module in reasoning_modules])
    return reasoning_modules_text

# Your DSPy Module class definitions...
class SelectReasoningModules(dspy.Signature):
    """Select several relevant reasoning modules that are crucial to utilize in order to solve the given task(s)."""

    task_description = dspy.InputField(prefix="Task(s) Description:", desc="The task(s) to solve.")
    reasoning_modules = dspy.InputField(
        prefix="Relevant Reasoning Modules:",
        desc="List of relevant reasoning modules to solve task(s) with.",
    )
    selected_reasoning_modules = dspy.OutputField(
        prefix="Selected Reasoning Modules and their Descriptions:",
        desc="Select several reasoning modules that are the most appropriate for solving the given task(s). Do NOT elaborate on why, just provide a list of `{module type}: {description}`.",
    )

class SelectReasoningModule(dspy.Module):
    def __init__(self, reasoning_modules):
        super().__init__()

        self.reasoning_modules = reasoning_modules
        self.generate = dspy.ChainOfThought(SelectReasoningModules)

    def forward(self, task_description: str) -> dspy.Prediction:
        prediction = self.generate(task_description=task_description, reasoning_modules=self.reasoning_modules)

        return prediction
class AdaptReasoningModules(dspy.Signature):
    """Rephrase and specify each selected reasoning module so that it better helps solving the given task(s)."""

    task_description = dspy.InputField(prefix="Task(s) Description:", desc="The task(s) to solve.")
    selected_reasoning_modules = dspy.InputField(
        prefix="Selected Reasoning Modules:",
        desc="The selected reasoning modules that will be adapted to solve the task(s).",
    )
    adapted_reasoning_modules = dspy.OutputField(
        prefix="Adapted Reasoning Modules:",
        desc="Adapt and tailor each selected reasoning module's description to better solve the task(s). Do NOT work out the full solution.",
    )


class AdaptReasoningModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(AdaptReasoningModules)

    def forward(self, task_description: str, selected_reasoning_modules: str) -> dspy.Prediction:
        prediction = self.generate(
            task_description=task_description,
            selected_reasoning_modules=selected_reasoning_modules,
        )
        return prediction
class ImplementReasoningStructures(dspy.Signature):
    """Operationalize each adapted reasoning module into a step-by-step structured reasoning plan template to solve the task(s)."""

    task_description = dspy.InputField(prefix="Task(s) Description:", desc="The task(s) to solve.")
    adapted_reasoning_modules = dspy.InputField(
        prefix="Task Adapted Reasoning Modules:",
        desc="The adapted reasoning modules that will be implemented to better solve the task(s).",
    )
    implemented_reasoning_structures = dspy.OutputField(
        prefix="Implemented Reasoning Structures:",
        desc="Implement a JSON-formmated reasoning structure template for solvers to follow step-by-step and arrive at correct answers. Do NOT work out the full solution.",
    )

class ImplementReasoningStructure(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(ImplementReasoningStructures)

    def forward(self, task_description: str, adapted_reasoning_modules: str) -> dspy.Prediction:
        prediction = self.generate(
            task_description=task_description,
            adapted_reasoning_modules=adapted_reasoning_modules,
        )
        return prediction
    
class ExecuteReasoningStructures(dspy.Signature):
    """Execute the given reasoning structure to solve a specific task(s)."""
    
    task_description = dspy.InputField(prefix="Task(s) Description:", desc="The task(s) to solve.")
    implemented_reasoning_structures = dspy.InputField(
        desc="The JSON-formatted reasoning structure template that will be used to solve the task(s).",
    )
    executed_reasoning_structures = dspy.OutputField(
        desc="Using the reasoning structure as a guide, solve the task(s) and provide the final answer(s).",
    )

class ExecuteReasoningStructure(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.Predict(ExecuteReasoningStructures)

    def forward(self, task_description: str, implemented_reasoning_structures: str) -> dspy.Prediction:
        prediction = self.generate(
            task_description=task_description,
            implemented_reasoning_structure=implemented_reasoning_structures,
        )
        return prediction
    
class SelfDiscover(dspy.Module):
    """A comprehensive DSPy module encapsulating the Self-Discover approach."""
    def __init__(self, reasoning_modules):
        super().__init__()
        self.reasoning_modules = reasoning_modules
        self.select_reasoning_module = SelectReasoningModule(reasoning_modules=self.reasoning_modules)
        self.adapt_reasoning_module = AdaptReasoningModule()
        self.implement_reasoning_module = ImplementReasoningStructure()
        self.execute_reasoning_structure = ExecuteReasoningStructure()

    def forward(self, task_description: str) -> dspy.Prediction:
        print(f"SelfDiscover forward called with task_description: {task_description}")

        # STAGE 1: SELECT
        selection_prediction = self.select_reasoning_module.forward(task_description)
        selected_reasoning_modules = selection_prediction.selected_reasoning_modules
        print(f"Selected reasoning modules: {selected_reasoning_modules}")

        # STAGE 2: ADAPT
        adaptation_prediction = self.adapt_reasoning_module.forward(task_description, selected_reasoning_modules)
        adapted_reasoning_modules = adaptation_prediction.adapted_reasoning_modules
        print(f"Adapted reasoning modules: {adapted_reasoning_modules}")

        # STAGE 3: IMPLEMENT
        implementation_prediction = self.implement_reasoning_module.forward(task_description, adapted_reasoning_modules)
        implemented_reasoning_structures = implementation_prediction.implemented_reasoning_structures
        print(f"Implemented reasoning structures: {implemented_reasoning_structures}")

        # STAGE 4: EXECUTE
        execution_prediction = self.execute_reasoning_structure.forward(task_description, implemented_reasoning_structures)
        executed_reasoning_structures = execution_prediction.executed_reasoning_structures
        print(f"Executed reasoning structures: {executed_reasoning_structures}")

        return dspy.Prediction(solution=executed_reasoning_structures)

    
@app.on_event("startup")
def startup_event():
    configure_dspy()
    # Load reasoning modules if they are to be used application-wide

# Example function to load reasoning modules based on task type
def load_reasoning_modules_for_task(task_type: str):
    # Define paths or logic to select the correct reasoning modules JSON
    reasoning_module_paths = {
        "math": "./reasoning_modules_math.json",
        "nlp": "./reasoning_modules_nlp.json",
        # Add more task types and corresponding module files as needed
    }
    json_file_path = reasoning_module_paths.get(task_type, "./default_reasoning_modules.json")
    with open(json_file_path, "r") as file:
        data = json.load(file)
    reasoning_modules = data.get("reasoning_modules", [])
    reasoning_modules_text = ", ".join([f'({module["type"]}: {module["description"]})' for module in reasoning_modules])
    return reasoning_modules_text

# Update the TaskRequest model to include a task_type field
class TaskRequest(BaseModel):
    description: str
    task_type: str  # Added field to specify the task type

@app.post("/solve-task/")
async def solve_task(request: TaskRequest):
    # Dynamically load reasoning modules based on the specified task type
    reasoning_modules_text = load_reasoning_modules_for_task(request.task_type)

    # Initialize the SelfDiscover module with the dynamically loaded reasoning modules
    self_discover = SelfDiscover(reasoning_modules=reasoning_modules_text)

    # Process the task using the SelfDiscover module
    prediction = self_discover.forward(task_description=request.description)
    
    # Return the prediction or solution
    return {"solution": prediction.solution}

@app.post("/execute-code/")
async def execute_code(request: CodeExecutionRequest):
    try:
        # Here, you use Open Interpreter to run the code
        execution_result = oi.chat(f"```python\n{request.code}\n```", display=False)
        return {"result": execution_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute code: {e}")

@app.post("/generate-and-execute/")
async def generate_and_execute(request: TaskRequest):
    print(f"generate-and-execute called with description: {request.description}, task_type: {request.task_type}")

    # Load reasoning modules based on task type.
    reasoning_modules_text = load_reasoning_modules_for_task(request.task_type)
    print(f"Loaded reasoning modules: {reasoning_modules_text}")

    # Use the SelfDiscover module to process the task.
    self_discover = SelfDiscover(reasoning_modules=reasoning_modules_text)
    prediction = self_discover.forward(task_description=request.description)
    print(f"Prediction from SelfDiscover: {prediction}")

    # Here, you'd need to extract the reasoning structure from the prediction.
    # The following is a placeholder - you'll need to adjust it based on your actual data structure:
    if hasattr(prediction, 'solution') and isinstance(prediction.solution, ReasoningStructure):
        reasoning_structure = prediction.solution
        print(f"Extracted reasoning structure: {reasoning_structure}")

        # Generate code using the GenerateCodeModule.
        generate_code_module = GenerateCodeModule()
        generated_code = generate_code_module.forward(reasoning_structure)
        print(f"Generated code: {generated_code}")

        try:
            execution_result = oi.chat(f"```python\n{generated_code}\n```", display=False)
            print(f"Execution result: {execution_result}")
            return {"result": execution_result}
        except Exception as e:
            print(f"Error executing code: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate or execute code: {e}")
    else:
        error_msg = "Failed to extract reasoning structure from prediction."
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)



if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8008, reload=True)
