from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.fridge_service import FridgeService
import sys

bookmarksBp = Blueprint('fridge_views', __name__)
