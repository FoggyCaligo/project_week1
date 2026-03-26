from flask import Blueprint, render_template, redirect, url_for, flash
from app.common import (
    requireLogin,
    getRecipeByID,
    getNextID,
    getNow,
    bookmarks,
    buildRecipeCard,
    formatDateTime,
)

bookmarks_bp = Blueprint("bookmarks", __name__)

@bookmarks_bp.route("/bookmarks/add/<recipeID>", methods=["POST"])
def addBookmark(recipeID: str):
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    recipeData = getRecipeByID(recipeID)
    if recipeData is None:
        flash("북마크할 레시피를 찾지 못했습니다.", "error")
        return redirect(url_for("main.recommendPage"))

    alreadyBookmarked = next(
        (
            item
            for item in bookmarks
            if item["userID"] == currentUser.ID and item["recipeID"] == recipeID
        ),
        None,
    )

    if alreadyBookmarked:
        flash("이미 북마크한 레시피입니다.", "info")
        return redirect(url_for("bookmarks.bookmarksPage"))

    bookmarks.append(
        {
            "id": getNextID(bookmarks),
            "userID": currentUser.ID,
            "recipeID": recipeID,
            "createdAt": getNow(),
        }
    )

    flash("북마크에 저장되었습니다.", "success")
    return redirect(url_for("bookmarks.bookmarksPage"))

@bookmarks_bp.route("/bookmarks")
def bookmarksPage():
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    userBookmarkList = sorted(
        [item for item in bookmarks if item["userID"] == currentUser.ID],
        key=lambda item: item["createdAt"],
        reverse=True,
    )

    bookmarkedRecipes = []
    for bookmarkData in userBookmarkList:
        recipeData = getRecipeByID(bookmarkData["recipeID"])
        if recipeData:
            recipeCard = buildRecipeCard(recipeData, currentUser.ID)
            recipeCard["createdAt"] = formatDateTime(bookmarkData["createdAt"])
            bookmarkedRecipes.append(recipeCard)

    return render_template("bookmarks.html", bookmarkedRecipes=bookmarkedRecipes)

@bookmarks_bp.route("/bookmarks/remove/<recipeID>", methods=["POST"])
def removeBookmark(recipeID: str):
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    targetBookmark = next(
        (
            item
            for item in bookmarks
            if item["userID"] == currentUser.ID and item["recipeID"] == recipeID
        ),
        None,
    )

    if targetBookmark is None:
        flash("삭제할 북마크를 찾지 못했습니다.", "error")
        return redirect(url_for("bookmarks.bookmarksPage"))

    bookmarks.remove(targetBookmark)
    flash("북마크가 삭제되었습니다.", "success")
    return redirect(url_for("bookmarks.bookmarksPage"))