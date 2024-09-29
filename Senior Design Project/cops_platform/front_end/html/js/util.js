function home() {
    window.location.href = "home.html";
}

function handleRejection(rejection) {
    var status = rejection.status;
    var text = rejection.statusText;
    var message = rejection.data ? rejection.data.message : "";

    var msg = "Response:\n";
    msg += `ERROR ${status}\n`;
    msg += `${text}\n`;
    msg += `${message}\n`;
    alert(msg);
}

function formify(data) {
    var form = "";
    for (var key in data) {
        form += `&${key}=${data[key]}`;
    }
    return form.substring(1);
}

function get(http, api, cookies) {
    http.defaults.withCredentials = true;
    var url = cookies.get("url");
    var request = {
        method: "GET",
        url: url + api,
    };
    return http(request);
}

function requestBody(http, api, data, method, cookies) {
    http.defaults.withCredentials = true;
    var url = cookies.get("url");
    var request = {
        method: method,
        url: url + api,
        headers: {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        data: formify(data)
    };
    return http(request);
}

function post(http, api, data, cookies) {
    return requestBody(http, api, data, "POST", cookies);
}

function del(http, api, data, cookies) {
    return requestBody(http, api, data, "DELETE", cookies);
}

function put(http, api, data, cookies) {
    return requestBody(http, api, data, "PUT", cookies);
}

function logout(http, cookies) {
    var method = "GET";
    var url = "/api/logout";

    get(http, url, cookies)
    .then(function(response) {
        console.log(response.data);
    })
    .catch(handleRejection)
    .finally(function() {
        cookies.remove("url");
        window.location.href="sso.html";
    });
}