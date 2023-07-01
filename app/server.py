from typing import Type

import pydantic
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from models import Session, Ad
from schema import CreateAd, UpdateAd

app = Flask("app")


class HTTPError(Exception):
    def __init__(self, status_code: int, message: str | list | dict):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(er: HttpError):
    response = jsonify({"status": "error", "message": er.message})
    response.status_code = er.status_code
    return response


def validate(validation_schema: Type[CreateAd], json_data):
    try:
        pydantic_obj = validation_schema(**json_data)
        return pydantic_obj.dict(exclude_none=True)
    except pydantic.ValidationError as er:
        raise HTTPError(400, er.errors())


class AdView(MethodView):
    def get(self, ad_id: int):
        with Session() as session:
            ad = session.query(Ad).filter(Ad.id == ad_id).first()
            if ad_id != Ad.id:
                raise HTTPError(400, "error")
            return jsonify(
                {
                    "id": ad.id,
                    "title": ad.title,
                    "created_at": ad.creation_time.isoformat(),
                    "description": ad.description,
                    "owner": ad.owner,
                }
            )

    def post(self):
        json_data = dict(request.json)
        try:
            json_data_validate = CreateAd(**json_data).dict()
        except pydantic.ValidationError as er:
            raise HTTPError(400, "error")

        with Session() as session:
            ads = Ad(**json_data_validate)
            session.add(ads)
            session.commit()
            return jsonify(
                {
                    "id": ads.id,
                    "title": ads.title,
                    "owner": ads.owner,
                    "description": ads.description,
                }
            )

    def patch(self, ad_id: str):
        ad_up = Ad.query.get(ad_id)
        if ad_up is not None:
            try:
                validate(request.json, UpdateAd)
            except pydantic.ValidationError as er:
                raise HTTPError(400, "error")

            if request.json.get("title"):
                ad_up.title = request.json.get("title")
            if request.json.get("description"):
                ad_up.description = request.json.get("description")
            session.commit()
            return jsonify(
                {
                    "id": ad_up.id,
                    "title": ad_up.title,
                    "description": ad_up.description,
                }
            )
        else:
            responce = jsonify({"error": "This ad does not exist"})
            responce.status_code = 404
            return responce

    def delete(self, ad_id: str):
        try:
            with Session() as session:
                ad = session.query(Ad).filter(Ad.id == ad_id).first()
                session.delete(ad)
                session.commit()
                return jsonify({"status": "deleted"})
        except pydantic.ValidationError as er:
            raise HTTPError(400, "error")

app.add_url_rule(
    "/ads/<int:ad_id>/", view_func=AdView.as_view("ads_delete"),
                 methods=["GET", "PATCH", "DELETE"]
)
app.add_url_rule(
    "/ads", view_func=AdView.as_view('ads_create'), methods=['POST']
)