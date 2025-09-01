from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Union, Sequence, cast

import colorama  # type: ignore[import-untyped]
from loguru import logger

from src.core.config import ConfigLoader
from src.core.utils import MethodTools
from .visma_integration import VismaIntegration
from src.services.http_clients.renderer_client import RendererHttpClient


class MathSolver:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        visma_timeout = self.config.get("visma", "timeout")
        self.visma_engine = VismaIntegration(timeout=visma_timeout)


    async def _render_one(self, expr: str, access_token: str) -> str:
        client = RendererHttpClient()
        return await client.render_latex_url(expr, access_token)


    async def _render_many(self, expressions: List[str], access_token: str) -> List[str]:
        client = RendererHttpClient()
        tasks = [client.render_latex_url(expr, access_token) for expr in expressions]
        urls = await asyncio.gather(*tasks, return_exceptions=False)
        return cast("List[str]", list(urls))


    async def _generate_renders_async(
        self,
        str_results: List[str],
        render_latex: bool,
        access_token: str,
    ) -> List[str]:

        if not render_latex:
            return ["None"] * len(str_results)
        if len(str_results) == 1:
            return [await self._render_one(str_results[0], access_token)]
        return await self._render_many(str_results, access_token)



    @logger.catch
    async def solve_math_expression(
        self,
        expression: str,
        show_solving_steps: bool,
        render_latex_expressions: bool,
        access_token: str,
    ) -> Dict[str, List[str]]:
        """
        Solve mathematical expression using Visma engine only.
        
        Args:
            expression: LaTeX mathematical expression
            show_solving_steps: Whether to include solving steps
            render_latex_expressions: Whether to render results as images
            access_token: Access token for renderer service
            
        Returns:
            Dictionary containing results, steps, and image URLs
        """
        try:
            
            operation = self._determine_operation(expression)
            
            visma_result = await self.visma_engine.solve_expression(
                latex_expression=expression,
                operation=operation,
                show_steps=show_solving_steps
            )
            
            results = cast("List[str]", visma_result["results"])
            solving_steps = cast("List[str]", visma_result["solving_steps"])
            
            images_urls = await self._generate_renders_async(results, render_latex_expressions, access_token)
            
            return {
                "results": results,
                "images_urls": images_urls,
                "solving_steps": solving_steps
            }
            
        except Exception as e:
            logger.error(f"Visma solving failed: {e}")
            return {
                "results": [expression],
                "images_urls": ["None"],
                "solving_steps": [f"Error: {str(e)}"]
            }
    
    def _determine_operation(self, expression: str) -> str:
        """
        Determine the best operation for the given expression.
        
        Args:
            expression: Mathematical expression
            
        Returns:
            Operation name
        """
        # Check for limit expressions first
        if '\\lim' in expression:
            return 'limit'
            
        if '=' in expression:
            if '^2' in expression or '^{2}' in expression:
                return 'find-roots'  
            return 'solve'
        
        if 'sqrt' in expression or '^' in expression:
            return 'factorize'
            
        return 'simplify'


