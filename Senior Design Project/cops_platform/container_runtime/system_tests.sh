function set_data {
  switch_to coordinator > /dev/null
  echo "SETTING UP SYSTEM FOR TESTING (errors are okay here)"
  echo "============================================================================================="
  add_user testuser0 "Test User 0" student
  add_user teststudent "Test Student" student
  add_user testinstructor "Test Instructor" instructor
  add_user testcoordinator "Test Coordinator" coordinator
  
  delete_user testuser1 student
  delete_user testuser2 instructor
  delete_user testuser3 coordinator
  
  delete_course testcourse0
  delete_course testcourse1
  delete_course testcourse2
  delete_course testcourse3
  
  add_course testcourse0 MW 2:00 3:00 instructor
  add_course testcourse1 TTh 3:00 4:00 instructor
  add_course testcourse2 MWF 5:00 6:00 instructor
  
  enroll_student testcourse0 testuser0
  echo "============================================================================================="
}

function run_tests() {
  set_data
  switch_to $1 > /dev/null
  echo "RUNNING API REQUESTS AS ${1^^}"
  echo "============================================================================================="
  echo "Viewing account info"
  account_info
  echo
  echo "Viewing schedule"
  schedule
  echo
  echo "Adding a student"
  add_user testuser1 "Test User 1" student
  echo
  echo "Adding an instructor"
  add_user testuser2 "Test User 2" instructor
  echo
  echo "Adding a coordinator"
  add_user testuser3 "Test User 3" coordinator
  echo
  echo "Deleting student"
  delete_user teststudent student
  echo
  echo "Deleting instructor"
  delete_user testinstructor instructor
  echo
  echo "Deleting coordinator"
  delete_user testcoordinator coordinator
  echo
  echo "Adding course"
  add_course testcourse3 F 6:00 7:00 instructor
  echo
  echo "Enrolling student in course"
  enroll_student testcourse2 student
  echo
  echo "Setting student grade"
  set_grade testcourse0 testuser0 4.0
  echo
  echo "Deleting course with no enrolled students"
  delete_course testcourse1
  echo
  echo "Deleting course with enrolled students"
  delete_course testcourse0
  echo
  echo "============================================================================================="
}

function wait_for_flask {
  kill_flask
  dots=1
  while ps | grep -q flask; do
    echo -en "\r                                 \r"
    echo -n "Waiting for flask to terminate"
    for i in `seq 1 $dots`; do
      echo -n "."
    done
    let dots="$dots % 3 + 1"
    sleep 1
  done
}

pwd
source ./flask_app.sh
source ./curl_shortcuts.sh > /dev/null

sudo systemctl restart postgres
sudo netlabelctl unlbl add default address:127.0.0.1 label:unconfined_u:unconfined_r:unconfined_t:s0

wait_for_flask
flask run > /dev/null &
echo "Sleeping for 3 seconds..."
sleep 3

echo "CONNECTING..."
echo "============================================================================================="
echo "Connecting as coordinator..."
connect_as coordinator > /dev/null

echo "Connecting as instructor..."
connect_as instructor > /dev/null

echo "Connecting as student..."
connect_as student > /dev/null
echo "============================================================================================="

run_tests coordinator
run_tests instructor
run_tests student

wait_for_flask
