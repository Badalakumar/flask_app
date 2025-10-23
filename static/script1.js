document.addEventListener('DOMContentLoaded', () => {
    // DOM Element References
    const addStudentBtn = document.getElementById('addStudentBtn');
    const studentFormModal = document.getElementById('studentFormModal');
    const closeBtn = document.querySelector('.close-btn');
    const studentForm = document.getElementById('studentForm');
    const studentTableBody = document.querySelector('#studentTable tbody');
    const formTitle = document.getElementById('formTitle');
    const studentIndexInput = document.getElementById('studentIndex');
    const submitButton = document.getElementById('submitButton');
    const subjectsContainer = document.getElementById('subjectsContainer');

    // Data Storage (Using an array to simulate a database)
    // NOTE: In a real application, you'd load this from a server/DB.
    let students = [];

    // Utility function to get checked subjects from the form
    const getSelectedSubjects = () => {
        const selected = [];
        subjectsContainer.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            if (checkbox.checked) {
                selected.push(checkbox.value);
            }
        });
        return selected.join(', '); // Store as a comma-separated string
    };

    // Utility function to set checkboxes based on stored subject string
    const setSelectedSubjects = (subjectString) => {
        const subjectsArray = subjectString.split(',').map(s => s.trim());
        subjectsContainer.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = subjectsArray.includes(checkbox.value);
        });
    };

    // --- Modal Control Functions ---

    /**
     * Shows the student form modal.
     * @param {string} mode - 'add' or 'edit'.
     */
    const showFormModal = (mode = 'add') => {
        if (mode === 'add') {
            formTitle.textContent = 'Add Student Details';
            submitButton.textContent = 'Submit';
            studentForm.reset();
            studentIndexInput.value = ''; // Clear index for a new student
            setSelectedSubjects(""); // Clear subjects for add mode
        }
        studentFormModal.style.display = 'block';
    };

    /**
     * Hides the student form modal.
     */
    const hideFormModal = () => {
        studentFormModal.style.display = 'none';
    };

    // Event Listeners for Modal
    addStudentBtn.addEventListener('click', () => showFormModal('add'));
    closeBtn.addEventListener('click', hideFormModal);

    // Hide modal if user clicks outside of it
    window.addEventListener('click', (event) => {
        if (event.target === studentFormModal) {
            hideFormModal();
        }
    });

    // --- Data Rendering and Handling ---

    /**
     * Renders the student array into the table.
     */
    const renderTable = () => {
        studentTableBody.innerHTML = ''; // Clear existing rows

        students.forEach((student, index) => {
            const row = studentTableBody.insertRow();
            
            // Student details columns
            const studentDetails = [
                student.adminName, student.name, student.emailId, student.phoneNo, student.gender,
                student.dob, student.className, student.department, student.subjects,
                student.fatherName, student.motherName, student.address
            ];

            studentDetails.forEach(detail => {
                const cell = row.insertCell();
                cell.textContent = detail;
            });

            // Is Active Toggle Column
            const activeCell = row.insertCell();
            activeCell.innerHTML = `
                <label class="switch">
                    <input type="checkbox" ${student.isActive ? 'checked' : ''} data-index="${index}">
                    <span class="slider"></span>
                </label>
            `;
            activeCell.querySelector('input').addEventListener('change', (e) => {
                students[index].isActive = e.target.checked;
            });

            // Actions (Edit Button) Column
            const actionsCell = row.insertCell();
            const editBtn = document.createElement('button');
            editBtn.textContent = 'Edit';
            editBtn.className = 'edit-btn';
            // Set up the event listener to call editStudent with the student's index
            editBtn.addEventListener('click', () => editStudent(index));
            actionsCell.appendChild(editBtn);
        });
    };

    /**
     * Handles the form submission (Add or Edit).
     */
    studentForm.addEventListener('submit', (e) => {
        e.preventDefault();

        // Collect all form data
        const formData = new FormData(studentForm);
        const studentData = Object.fromEntries(formData.entries());
        
        // Custom handling for multi-select (subjects)
        studentData.subjects = getSelectedSubjects();
        
        // Get the index from the hidden field
        const studentIndex = studentData.studentIndex;

        // Clean up the address field
        studentData.address = studentData.address.trim();

        if (studentIndex) {
            // EDIT/UPDATE existing student
            const index = parseInt(studentIndex);
            // Preserve the 'isActive' status from the existing record
            const isActive = students[index].isActive;
            students[index] = { ...studentData, isActive };
        } else {
            // ADD new student
            students.push({ ...studentData, isActive: true }); // Default to active
        }

        renderTable();
        hideFormModal();
    });

    /**
     * Loads the form with existing student data for editing.
     * @param {number} index - The index of the student in the array.
     */
    const editStudent = (index) => {
        const student = students[index];

        formTitle.textContent = 'Edit Student Details';
        submitButton.textContent = 'Update';
        studentIndexInput.value = index; // Store index for update logic

        // Populate the form fields
        document.getElementById('adminName').value = student.adminName;
        document.getElementById('name').value = student.name;
        document.getElementById('emailId').value = student.emailId;
        document.getElementById('phoneNo').value = student.phoneNo;
        document.getElementById('gender').value = student.gender;
        document.getElementById('dob').value = student.dob;
        document.getElementById('className').value = student.className;
        document.getElementById('department').value = student.department;
        document.getElementById('fatherName').value = student.fatherName;
        document.getElementById('motherName').value = student.motherName;
        document.getElementById('address').value = student.address;
        
        // Handle subjects (checkboxes)
        setSelectedSubjects(student.subjects); 

        showFormModal('edit');
    };
    
    // Initial render to show an empty table
    renderTable();
});