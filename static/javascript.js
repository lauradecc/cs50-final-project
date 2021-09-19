// Bookings page: Display text when button clicked
let button = document.getElementById('people-button');

// Ensure both functions work despite of being in same .js
if (button !== null) {

    button.addEventListener('click', function() {
        $.get('/people', function(people) {
            let html = '';
            for (let id in people) {
                let name = people[id].name;
                let surname = people[id].surname;
                html += '<li>' + name + ' ' + surname + '</li>';
            }
            document.getElementById('people').innerHTML = html;
        });
    });
}

// Show page: Display list when button clicked
let surprise = document.getElementById('discover-surprise');

// Ensure both functions work despite of being in same .js
if (surprise !== null) {

    surprise.addEventListener('click', function() {
        $.get('/surprise', function(snacks) {
            let html = '';
            for (let id in snacks) {
                let surprise = snacks[id].surprise;
                html += '<p>' + surprise + '<p>';
            }
            document.getElementById('surprise').innerHTML = html;
        });
    });
}
