# ******************************************************************************
#  *                              _Server_.py                                 *
#  *                                                                            *
#  *  Project: EyeMath                                                         *
#  *  Author: Usov Nikita                                                      *
#  *  Created: April 23, 2025                                                  *
#  *  Last Modified: May 05, 2025                                              *
#  *                                                                            *
#  *  Description:                                                             *
#  *  This is the Mathimatician Library with many of functions for EyeMath     *
#  *  Project. Here's some funtions how multiply, power, Generate LaTeX and  *
#  *  simpy recognize LaTeX code from PNG image.                               * 
#  *                                                                            *
#  ******************************************************************************


import _Math_Lib_ as MaL
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import toml
import subprocess
    



def INIT_SERVER():
    app = FastAPI()

    @app.get("/")
    def read_root():
        return (f"Hello World!")

    @app.get("/MaL/{operation}")
    def read_item(operation: str):
        print(f"Operation: {operation}")
        a = f"result: {MaL.solve_expression(operation)}"
        print(f"MaL answer: {a}")
        return a
    
    @app.get("/tasks")
    def get_tasks():
        task = Task(task="Solve x^2 + 2x + 1 = 0")
        print(task)
        return f"data: {task}"
        

    return app





if __name__ == "__main__" or "_Server_":

    class Task(BaseModel):
        task: str
        result: Optional[str] = None

    app = INIT_SERVER()
    