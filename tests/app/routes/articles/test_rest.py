import pytest
import uuid

from flask import json, url_for
from tests.conftest import create_authorization_header


sample_articles = [
    {
        "id": "1",
        "title": "Forty Years Fighting Racism and Intolerance",
        "author": "John Gilbert",
        "content": """<h2>A century with no solidarity</h2>\r\n One of the worst plagues that the twentieth century
        has had to \r\n bear is racial discrimination.""",
        "entrydate": "2015-11-01"
    },
    {
        "id": "2",
        "title": "Modern Mythology",
        "author": "Sabine Leitner",
        "content": """Despite their universal existence in all civilizations and all \r\ntimes of history,
        myths have often been scoffed at and regarded as old wives\u2019 \r\ntales.""",
        "entrydate": "2016-01-30"
    },
]


class WhenGettingArticles:

    def it_returns_all_articles(self, client, sample_article, db_session):
        response = client.get(
            url_for('articles.get_articles'),
            headers=[create_authorization_header()]
        )
        assert response.status_code == 200

        data = json.loads(response.get_data(as_text=True))

        assert len(data) == 1
        assert data[0]['id'] == str(sample_article.id)


class WhenGettingArticleByID:

    def it_returns_correct_article(self, client, sample_article, db_session):
        response = client.get(
            url_for('article.get_article_by_id', article_id=str(sample_article.id)),
            headers=[create_authorization_header()]
        )
        assert response.status_code == 200

        json_resp = json.loads(response.get_data(as_text=True))
        assert json_resp['id'] == str(sample_article.id)


class WhenPostingImportArticles(object):

    def it_creates_articles_for_imported_articles(self, client, db_session):
        response = client.post(
            url_for('articles.import_articles'),
            data=json.dumps(sample_articles),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_articles = json.loads(response.get_data(as_text=True))['articles']
        assert len(json_articles) == len(sample_articles)
        for i in range(0, len(sample_articles) - 1):
            assert json_articles[i]["old_id"] == int(sample_articles[i]["id"])
            assert json_articles[i]["title"] == sample_articles[i]["title"]
            assert json_articles[i]["author"] == sample_articles[i]["author"]
            assert json_articles[i]["content"] == sample_articles[i]["content"]
            assert json_articles[i]["created_at"] == sample_articles[i]["entrydate"]

    def it_does_not_create_article_for_imported_articles_with_duplicates(self, client, db_session):
        duplicate_article = {
            "id": "1",
            "title": "Forty Years Fighting Racism and Intolerance",
            "author": "John Gilbert",
            "content": """<h2>A century with no solidarity</h2>\r\n One of the worst plagues that the twentieth century
            has had to \r\n bear is racial discrimination.""",
            "entrydate": "2015-11-01"
        },

        sample_articles.extend(duplicate_article)

        response = client.post(
            url_for('articles.import_articles'),
            data=json.dumps(sample_articles),
            headers=[('Content-Type', 'application/json'), create_authorization_header()]
        )
        assert response.status_code == 201

        json_articles = json.loads(response.get_data(as_text=True))['articles']
        assert len(json_articles) == len(sample_articles) - 1  # don't add in duplicate article
        for i in range(0, len(sample_articles) - 1):
            assert json_articles[i]["old_id"] == int(sample_articles[i]["id"])
            assert json_articles[i]["title"] == sample_articles[i]["title"]
            assert json_articles[i]["author"] == sample_articles[i]["author"]
            assert json_articles[i]["content"] == sample_articles[i]["content"]
            assert json_articles[i]["created_at"] == sample_articles[i]["entrydate"]
