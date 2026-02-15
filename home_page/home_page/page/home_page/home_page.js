frappe.pages['home_page'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Home',
		single_column: true
	});

	// Hide the page head for a cleaner look
	$(wrapper).find('.page-head').hide();

	frappe.call({
		method: 'home_page.api.get_apps',
		callback: function(r) {
			if (r.message) {
				$(frappe.render_template('home_page', { apps: r.message })).appendTo(page.body);
			}
		}
	});
};
