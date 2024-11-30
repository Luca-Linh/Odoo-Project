from datetime import date, datetime

from odoo import http
from odoo.http import request, Response
import json

class EstatePropertyController(http.Controller):

    # @http.route('/vi', auth='public', type='http', website=True)
    # def homepage(self, **kwargs):
    #     return request.render('estate.homepage_template')

    @http.route('/estate_property', auth='public', type='http', website=True)
    def estate_property(self, page=1, search='', **kwargs):
        estates_per_page = 12
        page = int(page)

        domain = []
        if search:
            domain += [('name', 'ilike', search)]

        total_estates = request.env['estate.property'].sudo().search_count(domain)
        estates = request.env['estate.property'].sudo().search(
            domain, offset=(page - 1) * estates_per_page, limit=estates_per_page
        )

        pager = {
            'total': total_estates,
            'page': page,
            'per_page': estates_per_page,
            'pages': range(1, -(-total_estates // estates_per_page) + 1),  # Số lượng trang
            'prev': page - 1 if page > 1 else None,
            'next': page + 1 if page * estates_per_page < total_estates else None,
        }

        return request.render('estate.estates_page',{
            'estates': estates,
            'pager': pager,
            'search': search
        })

    # @http.route('/estate_property/<model("res.partner"):partner>', auth='public', type='http', website=True)
    # def estate_property_detail(self, estate_id):
    #     estate = request.env['estate.property'].sudo().browse(estate_id)
    #     if not estate.exists():
    #         return request.render('website.404')
    #     return request.render('estate.estate_details_page',{
    #         'estate':estate,
    #     })
    @http.route('/estate_property/<int:property_id>', auth='public', type='http', website=True)
    def estate_property_detail(self, property_id):
        estate = request.env['estate.property'].sudo().browse(property_id)
        if not estate.exists():
            return request.render('website.404')
        return request.render('estate.estate_details_page', {
            'estate': estate,
        })


def custom_serializer(obj):
    """Convert date/datetime to ISO format for JSON serialization."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

class EstateAPI(http.Controller):

    @http.route('/api/estate', auth='public', methods=['GET'], type='http')
    def get_estates(self, **kwargs):
        estate_id = kwargs.get('id')
        try:
            if estate_id:
                # Fetch estate by ID
                estate = request.env['estate.property'].sudo().browse(int(estate_id))
                if estate.exists():
                    all_fields = estate.fields_get().keys()
                    estate_data = estate.read(all_fields)[0]

                    # Serialize response
                    response = Response(
                        json.dumps({"status": "success", "data": estate_data}, default=custom_serializer),
                        content_type="application/json",
                        status=200
                    )
                    return response
                else:
                    # Estate not found
                    response = Response(
                        json.dumps({"status": "error", "message": "Estate not found"}),
                        content_type="application/json",
                        status=404
                    )
                    return response

            # Fetch all estates
            estates = request.env['estate.property'].sudo().search([])
            all_fields = estates.fields_get().keys()
            estate_data = estates.read(all_fields)

            # Serialize response
            response = Response(
                json.dumps({"status": "success", "data": estate_data}, default=custom_serializer),
                content_type="application/json",
                status=200
            )
            return response

        except ValueError:
            # Invalid estate ID
            response = Response(
                json.dumps({"status": "error", "message": "Invalid estate ID"}),
                content_type="application/json",
                status=400
            )
            return response
        except Exception as e:
            # Handle unexpected errors
            response = Response(
                json.dumps({"status": "error", "message": str(e)}),
                content_type="application/json",
                status=500
            )
            return response

    @http.route('/api/estate', auth='public', methods=['POST'], type='json')
    def create_estate(self, **kwargs):
        try:
            estate_data = request.jsonrequest
            # Validate required fields
            required_fields = ['name', 'property_type_id', 'expected_price']
            missing_fields = [field for field in required_fields if field not in estate_data]
            if missing_fields:
                return {
                "status": "error",
                "message": f"Missing fields: {', '.join(missing_fields)}"
            }
            # Create the estate property
            estate = request.env['estate.property'].sudo().create({
                'name': estate_data['name'],
                'property_type_id': estate_data['property_type_id'],
                'expected_price': estate_data['expected_price'],
                'living_area': estate_data['living_area'],
                'bedrooms': estate_data['bedrooms'],
                'postcode': estate_data['postcode']
            })
            # Return success response
            return {
                "status": "success",
                "message": "Estate created successfully",
                "data": {
                    "id": estate.id,
                    "name": estate.name
                }
            }
        except Exception as e:
            # Handle unexpected errors
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }

    @http.route('/api/estate/<int:estate_id>', auth='public', methods=['PUT'], type='json')
    def update_estate(self, estate_id, **kwargs):
        try:
            estate_data = request.jsonrequest

            estate = request.env['estate.property'].sudo().browse(estate_id)

            if not estate.exists():
                return {
                    "status":"error",
                    "message": "Estate not found"
                }, 404
            allowed_fields = ['name', 'property_type_id','expected_price', 'living_area', 'bedrooms', 'postcode']
            update_data = {key: value for key, value in estate_data.items() if key in allowed_fields}
            if not update_data:
                return {
                    "status": "error",
                    "message": "No valid fields provided for update"
                }, 400
            # update_data = {}
            # for field in allowed_fields:
            #     update_data[field] = estate_data.get(field, False)

            estate.update(update_data)
            return {
                "status": "success",
                "message": "Estate updated successfully",
                "data": estate.read(update_data)[0]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }, 500

    @http.route('/api/estate/<int:estate_id>', auth='public', methods=['PATCH'], type='json')
    def patch_estate(self, estate_id, **kwargs):
        try:
            # Parse the request data
            estate_data = request.jsonrequest

            # Fetch the estate to update
            estate = request.env['estate.property'].sudo().browse(estate_id)

            # Check if the estate exists
            if not estate.exists():
                return {
                    "status": "error",
                    "message": "Estate not found"
                }, 404

            # Validate payload: only include allowed fields
            allowed_fields = ['name', 'property_type_id', 'expected_price', 'living_area', 'bedrooms', 'postcode']
            update_data = {field: value for field, value in estate_data.items() if field in allowed_fields}

            # If no valid fields to update, return an error
            if not update_data:
                return {
                    "status": "error",
                    "message": "No valid fields to update"
                }, 400

            # Apply the updates
            estate.write(update_data)

            # Return the updated record
            return {
                "status": "success",
                "message": "Estate updated successfully",
                "data": estate.read(update_data)[0]
            }

        except Exception as e:
            return {
                    "status": "error",
                    "message": f"An error occurred: {str(e)}"
                },500

    @http.route('/api/estate', auth='public', methods=['DELETE'], type='http',csrf=False)
    def delete_estate(self, **kwargs):
        estate_id = kwargs.get('id')
        if not estate_id:
            return Response(
                json.dumps({"status": "error", "message": "Estate ID is required"}),
                content_type="application/json",
                status=400
            )

        try:
            estate = request.env['estate.property'].sudo().browse(int(estate_id))
            if estate.exists():
                estate.unlink()  # Delete the estate
                return Response(
                    json.dumps({"status": "success", "message": "Estate deleted successfully"}),
                    content_type="application/json",
                    status=200
                )
            else:
                return Response(
                    json.dumps({"status": "error", "message": "Estate not found"}),
                    content_type="application/json",
                    status=404
                )
        except ValueError:
            return Response(
                json.dumps({"status": "error", "message": "Invalid estate ID"}),
                content_type="application/json",
                status=400
            )
        except Exception as e:
            return Response(
                json.dumps({"status": "error", "message": str(e)}),
                content_type="application/json",
                status=500
            )


