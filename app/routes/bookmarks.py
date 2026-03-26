from flask import Blueprint, render_template, redirect, url_for, flash
from database import db
from app.common import requireLogin, getRecipeByID, buildRecipeCard, formatDateTime
from app.models.social import Bookmark

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

    existingBookmark = Bookmark.query.filter_by(
        userID=currentUser.ID,
        recipeID=recipeID
    ).first()

    if existingBookmark:
        flash("이미 북마크한 레시피입니다.", "info")
        return redirect(url_for("bookmarks.bookmarksPage"))

    newBookmark = Bookmark(
        userID=currentUser.ID,
        recipeID=recipeID
    )
    db.session.add(newBookmark)
    db.session.commit()

    flash("북마크에 저장되었습니다.", "success")
    return redirect(url_for("bookmarks.bookmarksPage"))

@bookmarks_bp.route("/bookmarks")
def bookmarksPage():
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    userBookmarkList = Bookmark.query.filter_by(
        userID=currentUser.ID
    ).order_by(Bookmark.createdAt.desc()).all()

    bookmarkedRecipes = []
    for bookmarkData in userBookmarkList:
        recipeData = getRecipeByID(bookmarkData.recipeID)
        if recipeData:
            recipeCard = buildRecipeCard(recipeData, currentUser.ID)
            recipeCard["createdAt"] = formatDateTime(bookmarkData.createdAt)
            bookmarkedRecipes.append(recipeCard)

    return render_template("bookmarks.html", bookmarkedRecipes=bookmarkedRecipes)

@bookmarks_bp.route("/bookmarks/remove/<recipeID>", methods=["POST"])
def removeBookmark(recipeID: str):
    currentUser, redirectResponse = requireLogin()
    if redirectResponse:
        return redirectResponse

    targetBookmark = Bookmark.query.filter_by(
        userID=currentUser.ID,
        recipeID=recipeID
    ).first()

    if targetBookmark is None:
        flash("삭제할 북마크를 찾지 못했습니다.", "error")
        return redirect(url_for("bookmarks.bookmarksPage"))

    db.session.delete(targetBookmark)
    db.session.commit()

    flash("북마크가 삭제되었습니다.", "success")
    return redirect(url_for("bookmarks.bookmarksPage"))