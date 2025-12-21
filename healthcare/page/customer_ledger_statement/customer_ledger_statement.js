frappe.pages['customer-ledger-statement'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('كشف حساب العميل'),
        single_column: true
    });

    const controls = {};
    const filter_area = $('<div class="customer-ledger-filters"></div>').appendTo(page.body);
    filter_area.css({
        background: '#f8fafc',
        borderRadius: '12px',
        padding: '16px',
        marginBottom: '20px',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '12px'
    });

    controls.customer = frappe.ui.form.make_control({
        parent: filter_area[0],
        df: {
            fieldtype: 'Link',
            options: 'Customer',
            label: __('Customer'),
            reqd: 1
        },
        render_input: true
    });

    controls.from_date = frappe.ui.form.make_control({
        parent: filter_area[0],
        df: {
            fieldtype: 'Date',
            label: __('From Date'),
            reqd: 1,
            default: frappe.datetime.month_start()
        },
        render_input: true
    });

    controls.to_date = frappe.ui.form.make_control({
        parent: filter_area[0],
        df: {
            fieldtype: 'Date',
            label: __('To Date'),
            reqd: 1,
            default: frappe.datetime.month_end()
        },
        render_input: true
    });

    const actions = $('<div class="mt-3"></div>').appendTo(page.body);
    const run_btn = $('<button class="btn btn-primary mr-2">'+__('عرض التقرير')+'</button>').appendTo(actions);
    const pdf_btn = $('<button class="btn btn-default">'+__('تحميل PDF')+'</button>').appendTo(actions);

    const result_wrapper = $('<div class="ledger-result mt-4"></div>').appendTo(page.body);

    const run_report = (download_pdf=false) => {
        const customer = controls.customer.get_value();
        const from_date = controls.from_date.get_value();
        const to_date = controls.to_date.get_value();

        if (!customer || !from_date || !to_date) {
            frappe.msgprint(__('Please fill all filters'));
            return;
        }

        frappe.call({
            method: 'custom_theme.api.erpnext_customer_statement_api.get_customer_statement',
            args: { customer, from_date, to_date },
            freeze: true,
            freeze_message: __('Generating statement...'),
            callback: function(r) {
                if (!r.exc) {
                    const payload = r.message;
                    result_wrapper.html(payload.html);

                    if (download_pdf) {
                        frappe.call({
                            method: 'healthcare.healthcare.page.customer_ledger_statement.customer_ledger_statement.download_pdf',
                            args: { customer, from_date, to_date },
                            callback: function(pdf_res) {
                                if (!pdf_res.exc) {
                                    const file_url = pdf_res.message;
                                    window.open(file_url, '_blank');
                                }
                            }
                        });
                    }
                }
            }
        });
    };

    run_btn.on('click', () => run_report(false));
    pdf_btn.on('click', () => run_report(true));
};
