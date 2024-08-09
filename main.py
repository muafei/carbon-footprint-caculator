import json


def load_material_ratios(filename='material_ratios.json'):
    """
    加载碳排放系数配置文件。

    参数:
        filename (str): JSON文件的路径。

    返回:
        dict: 包含碳排放系数的字典，分为能源、原材料和中间产品三个类别。
    """
    try:
        with open(filename, 'r') as file:
            material_ratios = json.load(file)
        return material_ratios
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not parse the JSON file '{filename}'.")
        return {}


def load_emission_factors(filename='carbon_footprint_config.json'):
    """
    加载碳排放系数配置文件。

    参数:
        filename (str): JSON文件的路径。

    返回:
        dict: 包含碳排放系数的字典，分为能源、原材料和中间产品三个类别。
    """
    try:
        with open(filename, 'r') as file:
            emission_factors = json.load(file)
        return emission_factors
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not parse the JSON file '{filename}'.")
        return {}


def get_raw_materials_for_intermediate(product_name):
    """
    返回生产一定量的中间产品所需的原材料的名称列表。

    :param product_name: 中间产品的名称
    :return: 原材料名称的列表
    """
    return list(load_material_ratios.get(product_name, {}).keys())


def get_raw_material_ratio(intermediate_product, raw_material):
    """
       返回生产一定量的中间产品所需某原材料的数量比例。

       :param intermediate_product: 中间产品的名称
       :param raw_material: 原材料的名称
       :return: 生产1单位中间产品所需原材料的比例
       """
    ratios = load_material_ratios.get(intermediate_product, {})
    ratio = ratios.get(raw_material, 0)
    return ratio


def calculate_emissions(usage, emission_factors):
    emissions = {}
    total_emission = 0
    consumed_raw_materials = {}

    # 计算能源的排放
    for resource, amount in usage.get('energy_sources', {}).items():
        if amount > 0 and resource in emission_factors.get('energy_sources', {}):
            emission = amount * emission_factors['energy_sources'][resource]
            emissions[resource] = emission
            total_emission += emission
            print(f"Energy source {resource}: {amount} units emitted {emission:.2f} kg CO₂e")
        elif amount == 0:
            emissions[resource] = 0  # 明确设置排放为0
        else:
            print(f"Warning: No emission factor found for {resource} in energy_sources.")

    # 先计算所有原材料的排放，避免重复
    for resource, amount in usage.get('raw_materials', {}).items():
        if amount > 0 and resource in emission_factors['raw_materials']:
            emission = amount * emission_factors['raw_materials'][resource]
            consumed_raw_materials[resource] = emission
            total_emission += emission
            print(f"Raw material {resource}: {amount} units emitted {emission:.2f} kg CO₂e")
        elif amount == 0:
            emissions[resource] = 0  # 明确设置排放为0
        else:
            print(f"Warning: No emission factor found for {resource}.")

            for resource, amount in usage.get('intermediate_products', {}).items():
                if amount > 0 and resource in emission_factors.get('intermediate_products', {}):
                    # 中间产品的直接排放
                    direct_emission = amount * emission_factors['intermediate_products'][resource]
                    total_emission += direct_emission
                    print(f"Intermediate product {resource}: {amount} units directly emitted {direct_emission:.2f} kg CO₂e")

                    # 获取中间产品的原材料并计算排放
                    for raw_material in get_raw_materials_for_intermediate(resource):
                        if amount * get_raw_material_ratio(resource, raw_material) > 0:
                            if raw_material in emission_factors['raw_materials']:
                                if raw_material not in consumed_raw_materials:
                                    # 使用原材料的比例来计算排放
                                    raw_material_emission = amount * get_raw_material_ratio(resource, raw_material) * \
                                                            emission_factors['raw_materials'][raw_material]
                                    consumed_raw_materials[raw_material] = raw_material_emission
                                    total_emission += raw_material_emission
                                    print(f"Intermediate product {resource} uses {raw_material}: "
                                          f"{amount * get_raw_material_ratio(resource, raw_material)} units emitted "
                                          f"{raw_material_emission:.2f} kg CO₂e")
                                elif amount * get_raw_material_ratio(resource, raw_material) == 0:
                                    emissions[raw_material] = emissions.get(raw_material, 0)
                                else:
                                    # 如果原材料已经被计算过，那么就不需要再次计算
                                    print(f"Material {raw_material} already accounted for in previous calculations.")
                        else:
                            print(f"Warning: No emission factor found for {raw_material}.")

            # 中间产品的总排放量等于直接排放加上所有相关原材料的排放
            emissions[resource] = direct_emission + sum(
                [consumed_raw_materials[mat] for mat in get_raw_materials_for_intermediate(resource)])
            print(f"Total emission for {resource}: {emissions[resource]:.2f} kg CO₂e")

    # 将所有计算的排放量合并到emissions字典中
    emissions.update(consumed_raw_materials)
    emissions['total'] = total_emission
    # 调用calculate_equivalent函数来计算等效的树木数量和人员数量
    tree_equivalent, person_equivalent = calculate_equivalent(total_emission)

    # 将等效值添加到emissions字典中
    emissions['tree_equivalent'] = tree_equivalent
    emissions['person_equivalent'] = person_equivalent
    print("Total calculated emissions:", emissions)
    return emissions


def calculate_equivalent(total_emission):
    # 假设每棵树每年可以吸收21kg CO₂
    carbon_absorbed_per_tree_per_year = 21
    # 全球人均碳排放量在2019年约为4.8吨二氧化碳当量（CO₂e），假设人均每天碳排放量10.1kg CO₂
    carbon_absorbed_per_person_per_year = 10.1
    tree_equivalent = total_emission / carbon_absorbed_per_tree_per_year
    person_equivalent = total_emission / carbon_absorbed_per_person_per_year
    return tree_equivalent, person_equivalent


# 示例：读取配置文件并计算碳排放量
if __name__ == "__main__":
    emission_factors = load_emission_factors()

    # 示例使用量
    usage = {
        'energy_sources': {
            'electricity': 100,  # 单位：kWh
            'natural_gas': 50  # 单位：m³
        },
        'raw_materials': {
            'aluminium': 20,  # 单位：kg
            'steel': 30  # 单位：kg
        },
        'intermediate_products': {
            'steel_sheets': 50,  # 单位：kg
            'aluminium_foil': 10  # 单位：kg
        }
    }

    results = calculate_emissions(usage, emission_factors)

    print("Individual carbon emissions:")
    for resource, emission in results.items():
        if resource != 'total':
            print(f"{resource}: {emission:.2f} kg CO₂e")
    print(f"Total carbon footprint: {results['total']:.2f} kg CO₂e")
