import os

import frappe


LOGO_FILENAMES = ("logo.png", "logo.svg", "logo.jpg", "icon.png", "icon.svg")


@frappe.whitelist()
def get_apps():
	"""Get installed apps with their public workspaces and icons."""
	installed_apps = frappe.get_installed_apps()
	apps = []

	for app in installed_apps:
		if app in ("frappe", "home_page"):
			continue

		hooks = frappe.get_hooks(app_name=app)
		app_title = hooks.get("app_title", [app])[0]

		# Get the modules this app declares
		modules = frappe.get_module_list(app)
		if not modules:
			continue

		# Find public workspaces belonging to those modules
		workspaces = frappe.get_all(
			"Workspace",
			filters={"module": ["in", modules], "public": 1},
			fields=["name", "title", "icon"],
			order_by="title",
		)

		if not workspaces:
			continue

		# Use the first workspace's icon as the app icon
		icon = workspaces[0].get("icon") or "grid"
		route = "/app/" + workspaces[0]["name"].lower().replace(" ", "-")

		# Check for a custom logo image in the app's public/images folder
		logo = _find_app_logo(app)

		apps.append({
			"name": app,
			"title": app_title,
			"icon": icon,
			"logo": logo,
			"route": route,
		})

	return apps


def _find_app_logo(app_name):
	"""Look for a logo image in <app>/public/images/. Returns asset URL or None."""
	try:
		app_path = frappe.get_app_path(app_name)
		images_dir = os.path.join(app_path, "public", "images")

		if not os.path.isdir(images_dir):
			return None

		for filename in LOGO_FILENAMES:
			if os.path.isfile(os.path.join(images_dir, filename)):
				return f"/assets/{app_name}/images/{filename}"

		return None
	except Exception:
		return None
