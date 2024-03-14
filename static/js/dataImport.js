let dataImportForm = document.getElementById("data-import-form");
let dataSubmissionBtn = document.getElementById("data-submission-btn");
let mappedHeadings = [];
var parsedData = [];

/*
This section reads the file and creates a mapper section
*/
dataImportForm.addEventListener("submit", (event) => {
  event.preventDefault();
  let file = document.getElementById("data-file")?.files[0];
  let fileUrl = URL.createObjectURL(file);
  Papa.parse(file, {
    complete: function (results) {
      parsedData = results.data;

      // creating objects from array
      const keys = parsedData[0];
      keys.forEach((key, index, keys) => {
        document.getElementById("field-mapping-body").innerHTML += `
          <div class='row form-group d-flex'>
            <div width="50%">${key}</div>
            <select onchange="onSelect(this,${index})" class='form-control'>
              <option value="None">Select An Option</option>
              {%for f in fields%}
              <option value={{f.id}}>{{f.title}}</option>
              {%endfor%}
            </select>
          </div>
          `;
      });
    },
  });
});

// mapping field to the table
const mapFields = () => {
  let table = document.createElement("table");
  table.classList.add("table");
  table.style.overflow = "scroll";

  let head = document.createElement("thead");
  head.classList.add("thead-dark");
  let headRow = document.createElement("tr");

  parsedData[0].forEach((headers) => {
    let th = document.createElement("th");
    th.textContent = headers;
    headRow.append(th);
  });

  head.appendChild(headRow);
  table.appendChild(head);
  let cleanedData = parsedData.filter((data) => data != parsedData[0]);
  cleanedData.forEach((rowData) => {
    let row = document.createElement("tr");
    rowData.forEach((cellData) => {
      let cell = document.createElement("td");
      cell.classList.add("table-cell");
      cell.textContent = cellData;
      row.appendChild(cell);
    });
    table.appendChild(row);
  });
  document.getElementById("table-data-body").appendChild(table);
};

const createData = async () => {
  const url = `${window.location.protocol}//${window.location.hostname}:${window.location.port}/form/import/data/`;
  const response = await fetch(url, {
    method: "POST",
    body: JSON.stringify(parsedData),
    headers: {
      Accept: "application/json, text/plain, */*",
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
  });
  console.log(await response.json());
};

dataSubmissionBtn.addEventListener("click", createData);

const onSelect = (obj, index) => {
  parsedData[0][index] = obj.value;
  document.getElementById("table-data-body").innerHTML = "";
  mapFields();
};
