$(document).on('page-change', function() {
	if (frappe.get_route_str() === 'Workspaces/Home Page') {
		frappe.set_route('home_page');
	}
});
