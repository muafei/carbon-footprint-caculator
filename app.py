from flask import Flask, request, jsonify
from flask_cors import CORS
from main import load_emission_factors, calculate_emissions

app = Flask(__name__)
CORS(app)  # 这将允许所有来源的跨域请求

@app.route('/calculate_emissions', methods=['POST'])
def calculate():
    try:
        # 验证请求体是否为JSON
        if not request.is_json:
            return jsonify({"error": "Request body must be JSON"}), 400

        usage = request.get_json()
        # 验证usage的结构和内容
        if not all(key in usage for key in ['energy_sources', 'raw_materials', 'intermediate_products']):
            return jsonify({"error": "Missing required fields in usage"}), 400

        # 加载排放因子，可以考虑缓存机制
        emission_factors = load_emission_factors()
        results = calculate_emissions(usage, emission_factors)
        return jsonify(results)

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True)