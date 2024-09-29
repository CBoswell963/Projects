# Defines some functions to allow for quick execution of curl commands to test container runtime and CourseManager
# Usage: source curl_shortcuts.sh 

function interface {
  echo
  echo "-----------------FUNCTIONS-----------------"
  echo "interface"
  echo "  - Print out this list of commands"
  echo
  echo "policy"
  echo "  - Quickly switch between the policy and container_runtime directories for policy development"
  echo
  echo "connect_as <username>"
  echo "  - Launch a container and log in as username"
  echo
  echo "connections"
  echo "  - List the usernames you've connected as. Note that failed connections will still be in this list"
  echo
  echo "switch_to <username>"
  echo "  - Switches your environment variables to send curl commands to the port associated with the username"
  echo
  echo "log_in"
  echo "  - Sends a login command to CourseManager as the current user"
  echo
  echo "account_info"
  echo "  - Information about the account of the current user"
  echo
  echo "add_user <username> \"<name>\" <role>"
  echo "  - Add a user to the database with the given username, full name, and role"
  echo
  echo "delete_user <username> <role>"
  echo "  - Delete the user with the given username and role"
  echo
  echo "add_course <name> <days> <start_time> <end_time> <instructor_username>"
  echo "  - Add a course with the given name, days of the week, start time, end time, and instructor username"
  echo
  echo "delete_course <name>"
  echo "  - Delete the course with the given name"
  echo
  echo "enroll_student <course_name> <student_username>"
  echo "  - Enroll the given student into the given course"
  echo
  echo "set_grade <course_name> <student_usernam> <grade 0-4.0>"
  echo "  - Set the grade for the given student in the given course to be the given grade"
  echo
  echo "log_out"
  echo "  - Send a logout to command to CourseManager as the current user"
  echo
  echo "kill_flask"
  echo "  - Sends a SIGINT to flask if running in the background. Also clears your list of connections"
  echo "-------------------------------------------"  
}

function policy {
  if [[ "$(pwd)" == *"container_runtime" ]]; then
    cd ../policies/course_manager
  elif [[ "$(pwd)" == *"policies/course_manager"* ]]; then
    cd ../../container_runtime
  else
    echo "Not in container_runtime or policy directory"
  fi
}

function connect_as() {
  response=$(curl -d "username=$1&service=course_manager" --cookie-jar ./terminal_cookie_$1 http://127.0.0.1:5000/service_request)
  local port=$(echo $response | ./get_port)
  echo
  if [ "$port" != "-1" ]; then
    idx=0
    local present=false
    for username in ${CM_USERNAMES[@]}; do
      if [ "$1" = "$username" ]; then
        present=true
        break
      fi
      ((idx++))
    done
    
    if [ "$present" = true ]; then
      PORTS[$idx]=$port
    else
      CM_USERNAMES=(${CM_USERNAMES[@]} $1)
      PORTS=(${PORTS[@]} $port)
    fi
    switch_to $1
  fi
  echo $response
}

function connections {
  local i=0
  for user in ${CM_USERNAMES[@]}; do
    echo "username: $user, port: ${PORTS[$i]}"
    ((i++))
  done
}

function switch_to() {
  local i=0
  for user in ${CM_USERNAMES[@]}; do
    if [ "$user" = "$1" ]; then
      CM_USERNAME=$user
      PORT=${PORTS[$i]}
      echo "Communicating as user $CM_USERNAME on port $PORT"
      return 0
    fi
    ((i++))
  done
  echo "Username: $1 not found"
}

function log_in {
  curl  -d "username=$CM_USERNAME" --cookie-jar ./terminal_cookie_$CM_USERNAME http://127.0.0.1:$PORT/api/login
}

function account_info {
  curl --cookie ./terminal_cookie_$CM_USERNAME --cookie-jar ./terminal_cookie_$CM_USERNAME http://127.0.0.1:$PORT/api/user
}

function add_user() {
  curl --cookie ./terminal_cookie_$CM_USERNAME -d "username=$1&name=$2&role=$3" --cookie-jar ./terminal_cookie_$CM_USERNAME http://127.0.0.1:$PORT/api/user
}

function delete_user() {
  curl -X DELETE --cookie ./terminal_cookie_$CM_USERNAME -d "username=$1&role=$2" --cookie-jar ./terminal_cookie_$CM_USERNAME http://127.0.0.1:$PORT/api/user
}

function add_course() {
  if [ "$#" -ne 5 ]; then
    echo "Usage: add_course <name> <days> <start_time> <end_time> <instructor_username>"
  fi
  curl  --cookie ./terminal_cookie_$CM_USERNAME -d "name=$1&days=$2&start_time=$3&end_time=$4&instructor_username=$5" --cookie-jar ./terminal_cookie_$CM_USERNAME http://127.0.0.1:$PORT/api/course
}

function delete_course() {
  curl -X DELETE --cookie ./terminal_cookie_$CM_USERNAME -d "course_name=$1" --cookie-jar ./terminal_cookie_$CM_USERNAME http://127.0.0.1:$PORT/api/course
}

function enroll_student() {
  curl --cookie ./terminal_cookie_$CM_USERNAME -d "course_name=$1&username=$2" --cookie-jar ./terminal_cookie_$CM_USERNAME http://127.0.0.1:$PORT/api/mapping
}

function set_grade() {
  curl -X PUT --cookie ./terminal_cookie_$CM_USERNAME -d "course_name=$1&username=$2&grade=$3" --cookie-jar ./terminal_cookie_$CM_USERNAME http://127.0.0.1:$PORT/api/mapping/grade
}

function schedule {
  curl --cookie ./terminal_cookie_$CM_USERNAME --cookie-jar ./terminal_cookie_$CM_USERNAME http://127.0.0.1:$PORT/api/schedule
}

function log_out {
  curl --cookie ./terminal_cookie_$CM_USERNAME http://127.0.0.1:$PORT/api/logout
}

function kill_flask {
  echo "Clearing list of connections..."
  CM_USERNAMES=()
  PORTS=()
  kill -2 $(pgrep -u maintuser flask)
}

interface
