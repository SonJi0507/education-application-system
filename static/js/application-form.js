const SUCCESS_MESSAGE = "신청이 접수되었습니다. 입력한 이메일로 확인 메일을 보냈습니다.";

const form = document.querySelector("#application-form");

if (form instanceof HTMLFormElement) {
  const submitButton = form.querySelector("[type='submit']");

  document.addEventListener(
    "blur",
    (event) => {
      syncAria(event.target);
    },
    true,
  );

  document.addEventListener("input", (event) => {
    const target = event.target;
    if (!isField(target) || !form.contains(target)) {
      return;
    }
    delete target.dataset.serverInvalid;
    const error = document.getElementById(`${target.id}-error`);
    if (error instanceof HTMLElement && error.dataset.clientMessage) {
      error.textContent = error.dataset.clientMessage;
      error.classList.remove("is-server");
    }
    syncAria(target);
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!(submitButton instanceof HTMLButtonElement)) {
      return;
    }
    submitButton.disabled = true;
    const status = document.getElementById("application-status");
    if (status) {
      status.textContent = "";
    }

    try {
      const response = await fetch(form.action, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken(form),
        },
        body: JSON.stringify(applicationPayload(form)),
      });
      const payload = await response.json();
      if (response.ok) {
        replaceForm(form);
        return;
      }
      showErrors(form, payload && typeof payload === "object" ? payload : {});
    } catch {
      if (status) {
        status.textContent = "신청을 보내지 못했습니다. 다시 시도해 주세요.";
      }
    } finally {
      if (submitButton.isConnected) {
        submitButton.disabled = false;
      }
    }
  });
}

function csrfToken(form) {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/);
  if (match) {
    return decodeURIComponent(match[1]);
  }
  const input = form.querySelector("[name='csrfmiddlewaretoken']");
  return input instanceof HTMLInputElement ? input.value : "";
}

function applicationPayload(form) {
  const data = new FormData(form);
  return {
    course: Number(data.get("course")),
    name: String(data.get("name") ?? ""),
    email: String(data.get("email") ?? ""),
    address: String(data.get("address") ?? ""),
    contact_date: String(data.get("contact_date") ?? ""),
  };
}

function isField(target) {
  return target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement;
}

function syncAria(target) {
  if (!isField(target) || target.dataset.serverInvalid === "true") {
    return;
  }
  if (target.matches(":user-invalid")) {
    target.setAttribute("aria-invalid", "true");
  } else {
    target.removeAttribute("aria-invalid");
  }
}

function messageOf(value) {
  if (typeof value === "string") {
    return value;
  }
  if (Array.isArray(value)) {
    return value.map(messageOf).find((item) => item) ?? "";
  }
  return "";
}

function showErrors(form, errors) {
  const status = document.getElementById("application-status");
  if (status) {
    status.textContent =
      messageOf(errors.detail) || messageOf(errors.non_field_errors) || messageOf(errors.course);
  }

  let firstInvalid = null;
  for (const target of form.querySelectorAll("input, textarea")) {
    if (!isField(target) || target.type === "hidden" || target.name === "csrfmiddlewaretoken") {
      continue;
    }
    const message = messageOf(errors[target.name]);
    const error = document.getElementById(`${target.id}-error`);
    if (!(error instanceof HTMLElement)) {
      continue;
    }
    if (message) {
      error.textContent = message;
      error.classList.add("is-server");
      target.dataset.serverInvalid = "true";
      target.setAttribute("aria-invalid", "true");
      firstInvalid ??= target;
    } else {
      error.textContent = error.dataset.clientMessage ?? "";
      error.classList.remove("is-server");
      delete target.dataset.serverInvalid;
      target.removeAttribute("aria-invalid");
    }
  }
  firstInvalid?.focus();
}

function replaceForm(form) {
  const panel = document.createElement("div");
  panel.className = "apply-success";
  panel.tabIndex = -1;
  const heading = document.createElement("h3");
  heading.textContent = "신청이 접수되었습니다";
  const paragraph = document.createElement("p");
  paragraph.textContent = SUCCESS_MESSAGE;
  panel.append(heading, paragraph);
  form.replaceWith(panel);
  panel.focus();
}
