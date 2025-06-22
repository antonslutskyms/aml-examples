import logging
import os
import re
import tempfile
from io import BytesIO
from typing import Annotated
import io
import sys

from semantic_kernel.kernel_pydantic import KernelBaseModel
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.exceptions.function_exceptions import FunctionExecutionException

from semantic_kernel.contents import ChatMessageContent, TextContent, ImageContent
from semantic_kernel.contents.utils.author_role import AuthorRole

import kernel_services
from datetime import datetime

logger = logging.getLogger(__name__)

class LocalPythonPlugin(KernelBaseModel):
    """
    A plugin that executes Python code locally with unrestricted access to built-in functions.
    WARNING: This plugin allows unrestricted access to built-in functions and should be used with caution.
    """

    def _set_output_dir(self, output_dir):
        self._output_dir = output_dir

    # region Helper Methods
    def _sanitize_input(self, code: str) -> str:
        """Sanitize input to the python REPL.

        Remove whitespace, backtick & python (if llm mistakes python console as terminal).

        Args:
            code (str): The query to sanitize
        Returns:
            str: The sanitized query
        """
        # Removes `, whitespace & python from start
        code = re.sub(r"^(\s|`)*(?i:python)?\s*", "", code)
        # Removes whitespace & ` from end
        return re.sub(r"(\s|`)*$", "", code)

    def _construct_remote_file_path(self, remote_file_path: str) -> str:
        """Construct the remote file path.

        Args:
            remote_file_path (str): The remote file path.

        Returns:
            str: The remote file path.
        """
        if not remote_file_path.startswith("/tmp/"):
            remote_file_path = f"/tmp/{remote_file_path}"
        return remote_file_path

    # endregion

    # region Kernel Functions
    @kernel_function(
        description="""Executes the provided Python code.
                     Start and end the code snippet with double quotes to define it as a string.
                     Insert \\n within the string wherever a new line should appear.
                     Add spaces directly after \\n sequences to replicate indentation.
                     Use \" to include double quotes within the code without ending the string.
                     Keep everything in a single line; the \\n sequences will represent line breaks
                     when the string is processed or displayed.
                     WARNING: This plugin allows unrestricted access to built-in functions and should be used with caution.
                     """,
        name="execute_code",
    )
    def execute_code(self, code: Annotated[str, "The valid Python code to execute"]) -> str:
        """Executes the provided Python code.

        Args:
            code (str): The valid Python code to execute
        Returns:
            str: The result of the Python code execution in the form of Result, Stdout, and Stderr
        Raises:
            FunctionExecutionException: If the provided code is empty.
        """
        if not code:
            raise FunctionExecutionException("The provided code is empty")

        code = self._sanitize_input(code)

        logger.info(f"Executing Python code: {code}")

#        try:
        # Save the code to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(code.encode())
            temp_file_path = temp_file.name

        # Log the generated code
        logger.info(f"Generated code:\n{code}")

        now = datetime.now()
        code_id = f"pro_{now.strftime('%Y%m%d%H%M%S')}"

        code_dir = f"{self._output_dir}/code"
        os.makedirs(code_dir, exist_ok=True)

        generated_code_file = f"{code_dir}/generated_code_{code_id}.py"

        # Save the generated code to a file
        with open(generated_code_file, "w") as file:
            file.write(code)

            
        print(f"Generated code:\n{code}")

        # Unrestricted execution: Allow all built-in functions
        safe_globals = {"__builtins__": __builtins__}  # Allow all built-ins
        safe_locals = {}  # Create a local execution scope

        print("\nWARNING: local_python_plugin is executing AI generated python code")
        # Read the code from the temporary file and execute it safely

        #generated_code_file = "./output/pro_202505291705/generated_code.py"
        print("generated_code_file", generated_code_file)
        with open(generated_code_file, "r") as file:
            read_code = file.read()
            # tabbed_read_code = read_code.replace('\n', '\n\t')

            code_template = read_code
#             f"""
# import sys
# try:
#     print('Executing generated code:...')
#     def _func_to_run():
#         return \ 
#         {tabbed_read_code}

#     _func_result = _func_to_run()
#     print('Generated code executed successfully!')
#     print(f'Code execution result:', _func_result)
# except:
#     print('Exception executing code: ', sys.exc_info())
#             """

            print(f"Calling eval() with code -----------------------------------\n:{code_template}")

            kernel_services.chat_history.add_message(ChatMessageContent(
                role=AuthorRole.ASSISTANT,
                items=[TextContent(text=code_template)]
            ))

            stdout_capture = io.StringIO()
            stdout_capture_err = io.StringIO()

            sys.stdout = stdout_capture
            sys.stderr = stdout_capture_err
            try:
                # EXEC EXEC EXEC
                exec(read_code, safe_globals, safe_locals)
            except:
                print('Exception executing code: ', sys.exc_info())
            finally:
                # Reset sys.stdout to its original state
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

            # Get the captured output
            captured_output = stdout_capture.getvalue()
            stdout_capture.close()

            captured_output_err = stdout_capture_err.getvalue()
            stdout_capture_err.close()

            print("Captured Output:")
            print(captured_output)
            if captured_output:
                kernel_services.chat_history.add_message(ChatMessageContent(
                                                    role=AuthorRole.ASSISTANT,
                                                    items=[TextContent(
                                                                metadata = {"source" : "python"},
                                                                text=captured_output)]
                                                ))

            
            print("Captured Error:")
            print(captured_output_err)
            if captured_output_err:
                kernel_services.chat_history.add_message(ChatMessageContent(
                                                    role=AuthorRole.ASSISTANT,
                                                    items=[TextContent(
                                                        metadata = {"source" : "python"},
                                                        text=captured_output_err)]
                                                ))

            print("WARNING: done executing AI generated python code")

            return f"{captured_output}{captured_output_err}"