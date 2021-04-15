"""Supercharged requests to handle errors from the API."""
from .supercharged_requests import load, requests, save

load()
__all__ = ["requests", "save"]
