document.addEventListener('DOMContentLoaded', function() {
    const ppaModal = document.getElementById('ppaModal');
    const deleteModal = document.getElementById('deleteModal');
    const ppaForm = document.getElementById('ppaForm');
    const modalTitle = document.getElementById('modalTitle');
    const formAction = document.getElementById('formAction');
    const ppaId = document.getElementById('ppaId');
    const ppaSlug = document.getElementById('ppaSlug');
    const deletePpaId = document.getElementById('deletePpaId');
    const deletePpaTitle = document.getElementById('deletePpaTitle');

    // Function to open the create modal
    window.openCreateModal = function() {
        modalTitle.textContent = 'Add New PPA';
        formAction.value = 'create';
        ppaId.value = '';
        ppaSlug.value = '';
        ppaForm.reset(); // Clear form fields
        // Set default values for new PPA
        document.getElementById('status').value = 'active';
        document.getElementById('priority_level').value = 'medium';
        ppaModal.classList.remove('hidden');
    }

    // Function to open the edit modal
    window.openEditModal = function(id) {
        modalTitle.textContent = 'Edit PPA';
        formAction.value = 'update';
        ppaId.value = id;
        
        // Fetch PPA data from the hidden script tag
        const ppaDataScript = document.getElementById(`ppa-data-${id}`);
        if (ppaDataScript) {
            const ppa = JSON.parse(ppaDataScript.textContent);
            document.getElementById('title').value = ppa.title;
            document.getElementById('ministry').value = ppa.ministry;
            document.getElementById('program_source').value = ppa.program_source;
            document.getElementById('ppa_type').value = ppa.ppa_type;
            document.getElementById('status').value = ppa.status;
            document.getElementById('priority_level').value = ppa.priority_level;
            document.getElementById('total_budget').value = ppa.total_budget;
            document.getElementById('start_date').value = ppa.start_date;
            document.getElementById('end_date').value = ppa.end_date;
            document.getElementById('geographic_coverage').value = ppa.geographic_coverage;
            document.getElementById('target_beneficiaries').value = ppa.target_beneficiaries;
            document.getElementById('description').value = ppa.description;
            document.getElementById('objectives').value = ppa.objectives;
            document.getElementById('expected_outcomes').value = ppa.expected_outcomes;
            document.getElementById('key_performance_indicators').value = ppa.key_performance_indicators;
            document.getElementById('implementation_strategy').value = ppa.implementation_strategy;
            document.getElementById('implementing_units').value = ppa.implementing_units;
            document.getElementById('funding_source').value = ppa.funding_source;
            ppaSlug.value = ppa.slug; // Set slug for potential use
        }
        ppaModal.classList.remove('hidden');
    }

    // Function to close the modal
    window.closeModal = function() {
        ppaModal.classList.add('hidden');
        ppaForm.reset();
    }

    // Function to confirm deletion
    window.confirmDelete = function(id, title) {
        deletePpaId.value = id;
        deletePpaTitle.textContent = title;
        deleteModal.classList.remove('hidden');
    }

    // Function to close delete modal
    window.closeDeleteModal = function() {
        deleteModal.classList.add('hidden');
    }

    // Function to submit delete form
    window.submitDelete = function() {
        document.getElementById('deleteForm').submit();
    }

    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target == ppaModal) {
            closeModal();
        }
        if (event.target == deleteModal) {
            closeDeleteModal();
        }
    });

    // Handle form submission via AJAX (optional, for smoother UX)
    // ppaForm.addEventListener('submit', function(e) {
    //     e.preventDefault();
    //     const formData = new FormData(ppaForm);
    //     fetch(ppaForm.action, {
    //         method: 'POST',
    //         body: formData,
    //         headers: {
    //             'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    //         }
    //     })
    //     .then(response => response.json())
    //     .then(data => {
    //         if (data.success) {
    //             alert(data.message);
    //             closeModal();
    //             location.reload(); // Reload page to see changes
    //         } else {
    //             alert('Error: ' + JSON.stringify(data.errors || data.error));
    //         }
    //     })
    //     .catch(error => {
    //         console.error('Error:', error);
    //         alert('An error occurred while saving the PPA.');
    //     });
    // });
});
