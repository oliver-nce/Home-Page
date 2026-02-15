import os

import frappe


LOGO_FILENAMES = ("logo.png", "logo.svg", "logo.jpg", "icon.png", "icon.svg")


@frappe.whitelist()
def get_apps():
	"""Get installed apps with their routes and icons.

	Resolution order for each app:
	1. add_to_apps_screen hook — route and logo defined by the app itself
	2. Public Workspace matching the app's modules
	3. Page matching the app name slug
	"""
	installed_apps = frappe.get_installed_apps()
	apps = []

	for app in installed_apps:
		if app in ("frappe", "home_page"):
			continue

		hooks = frappe.get_hooks(app_name=app)
		app_title = hooks.get("app_title", [app])[0]

		route = None
		icon = "grid"
		logo = None

		# 1. Check add_to_apps_screen hook (most reliable)
		apps_screen = hooks.get("add_to_apps_screen")
		if apps_screen:
			entry = apps_screen[0] if isinstance(apps_screen[0], dict) else None
			if entry:
				route = entry.get("route")
				logo = entry.get("logo")
				icon = entry.get("icon") or icon

		# 2. Fall back to public Workspace for this app's modules
		if not route:
			modules = frappe.get_module_list(app)
			if modules:
				workspaces = frappe.get_all(
					"Workspace",
					filters={"module": ["in", modules], "public": 1},
					fields=["name", "title", "icon"],
					order_by="title",
				)
				if workspaces:
					icon = workspaces[0].get("icon") or icon
					route = "/app/" + workspaces[0]["name"].lower().replace(" ", "-")

		# 3. Fall back to a Page matching the app name slug
		if not route:
			page_name = app.replace("_", "-")
			if frappe.db.exists("Page", page_name):
				route = "/app/" + page_name

		# Skip apps with no discoverable route
		if not route:
			continue

		# Verify hook logo exists on disk, fall back to filesystem search
		if logo and not _logo_exists(app, logo):
			logo = None
		if not logo:
			logo = _find_app_logo(app)

		apps.append({
			"name": app,
			"title": app_title,
			"icon": icon,
			"logo": logo,
			"route": route,
		})

	# Add static system entries
	apps.append({
		"name": "admin",
		"title": "Admin",
		"icon": "setting",
		"logo": "/assets/home_page/images/admin.png",
		"route": "/app/admin",
	})

	apps.append({
		"name": "advanced",
		"title": "Advanced",
		"icon": "tool",
		"logo": "/assets/home_page/images/advanced.png",
		"route": "/app/build",
	})

	return apps


def _logo_exists(app_name, logo_url):
	"""Check if a logo URL (e.g. /assets/app/logo.svg) actually exists on disk."""
	try:
		# logo_url is like /assets/app_name/images/logo.svg
		# maps to <app_path>/public/images/logo.svg
		if not logo_url or not logo_url.startswith(f"/assets/{app_name}/"):
			return False
		relative = logo_url.replace(f"/assets/{app_name}/", "")
		app_path = frappe.get_app_path(app_name)
		return os.path.isfile(os.path.join(app_path, "public", relative))
	except Exception:
		return False


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
