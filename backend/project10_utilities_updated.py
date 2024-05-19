from project10_db import *
from peewee import IntegrityError


def add_full_recipe(recipe_data):
    try:
        with db.atomic():
            category, _ = RecipeCategory.get_or_create(name=recipe_data['category_name'])

            recipe = Recipe.create(
                name=recipe_data['name'],
                category=category,
                difficulty=recipe_data['difficulty'],
                execution_time=recipe_data['execution_time']
            )

            for step_data in recipe_data['steps']:
                ingredient, _ = Ingredient.get_or_create(name=step_data['ingredient_name'])
                step = Step.create(
                    recipe_id=recipe,
                    title=step_data['title'],
                    description=step_data['description'],
                    number=step_data['number'],
                    execution_time=step_data['step_execution_time']
                )

                RecipesIngredients.create(
                    recipe_id=recipe,
                    ingredient_id=ingredient,
                    step_id=step,
                    quantity=step_data['ingredient_quantity']
                )

        return {"success": True, "message": "Recipe and details added successfully."}

    except IntegrityError as e:
        return {"success": False, "message": f"Database error: {e}"}

    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


recipe_dt = {
    'name': 'Carbonara',
    'category_name': 'Pasta',
    'difficulty': 2,
    'execution_time': 20,  # in minutes
    'steps': [
        {'title': 'Prepare Ingredients',
         'description': 'Measure all the ingredients.',
         'ingredient_name': 'Spaghetti',
         'ingredient_quantity': 100,  # grams
         'number': 1,
         'step_execution_time': 5},  # in minutes
        {'title': 'Cook Pasta',
         'description': 'Boil water and cook pasta.',
         'ingredient_name': 'Water',
         'ingredient_quantity': 1000,  # ml
         'number': 2,
         'step_execution_time': 10}
    ]
}

add_full_recipe(recipe_dt)


def search_recipe(name=None, category=None):
    try:
        query = Recipe.select()

        if name:
            query = query.where(Recipe.name.contains(name))

        if category:
            query = query.join(RecipeCategory).where(RecipeCategory.name.contains(category))

        recipes = list(query)

        if recipes:
            return {"success": True, "recipes": [{"id": recipe.id, "name": recipe.name, "category":
                    recipe.category.name, "difficulty": recipe.difficulty, "execution_time": recipe.execution_time}
                    for recipe in recipes]}

        else:
            return {"success": False, "message": "No recipes found."}

    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def edit_delete(recipe_id, action, updated_data=None, step_id=None, step_data=None, ingredient_data=None):
    try:
        recipe = Recipe.get_by_id(recipe_id)

        if action == 'update_recipe':

            if updated_data:
                Recipe.update(**updated_data).where(Recipe.id == recipe_id).execute()
            message = "Recipe updated successfully."

        elif action == "update_step":

            if step_id and step_data:
                Step.update(**step_data).where(Step.id == step_id).execute()
                message = "Step updated successfully."

            else:
                raise ValueError("Step ID and data required for updating a step.")

        elif action == "update_ingredient":

            if ingredient_data:
                RecipesIngredients.update(
                    **ingredient_data).where(
                    (RecipesIngredients.recipe == recipe_id) &
                    (RecipesIngredients.step == step_id) &
                    (RecipesIngredients.ingredient == ingredient_data["ingredient_id"])).execute()
                message = "Ingredient updated successfully."

            else:
                raise ValueError("Ingredient data is required for updating an ingredient.")

        elif action == 'delete_recipe':
            recipe.delete_instance(recursive=True)
            message = "Recipe deleted successfully."

        elif action == 'delete_step':
            if step_id:
                step = Step.get_by_id(step_id)
                step.delete_instance(recursive=True)
                message = "Step deleted successfully."

            else:
                raise ValueError("Step ID is required for deleting a step.")

        else:
            return {"success": False, "message": "Invalid action specified."}

        return {"success": True, "message": message}

    except Recipe.DoesNotExist:
        return {"success": False, "message": "Recipe does not exist."}

    except Step.DoesNotExist:
        return {"success": False, "message": "Step does not exist."}

    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}


def execute_recipe(recipe_id):
    try:
        recipe = Recipe.get_by_id(recipe_id)

        steps = (Step.select().where(Step.recipe_id == recipe_id).order_by(Step.number))

        total_time = recipe.execution_time
        cumulative_time = 0

        steps_details = []

        for step in steps:
            cumulative_time += step.execution_time
            completion_percentage = (cumulative_time / total_time) * 100

            step_details = {
                "title": step.title,
                "description": step.description,
                "step_execution_time": step.execution_time,
                "completion_percentage": round(completion_percentage, 2)
            }
            steps_details.append(step_details)

        return {"success": True, "steps": steps_details}

    except Recipe.DoesNotExist:
        return {"success": False, "message": "Recipe does not exist."}

    except Exception as e:
        return {"success": False, "message": f"Error: {e}"}
