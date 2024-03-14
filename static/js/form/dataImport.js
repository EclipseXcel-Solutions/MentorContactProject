let dataImportForm = document.getElementById("data-import-form");
let dataSubmissionBtn = document.getElementById("data-submission-btn");
let mappedHeadings = [];
var parsedData = [];

/*
This section reads the file and creates a mapper section
*/

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

const onSelect = (obj, index) => {
  parsedData[0][index] = Number(obj.value);
  document.getElementById("table-data-body").innerHTML = "";
  mapFields();
};

function prepareData() {
  const preparedData = [];
  const data = [...parsedData];
  const mapKeys = data[0];
  const dataToPrepare = data.filter((d) => d != mapKeys);

  dataToPrepare.forEach((item, index, array) => {
    const formData = [];
    mapKeys.forEach((mapItem, index, array) => {
      console.log(typeof mapItem, mapItem);
      if (typeof mapItem == "number") {
        const finalObj = {
          field: mapItem,
          array_answer: [item[index]?.split(",")],
          form: "{{form}}",
          section: "{{section}}",
          submission: "",
        };
        formData.push(finalObj);
      }
    });
    preparedData.push(formData);
  });
  return preparedData;
}
const submitData = async () => {
  const url = `${window.location.protocol}//${window.location.hostname}:${window.location.port}/form/import/data/`;
  const response = await fetch(url, {
    method: "POST",
    body: JSON.stringify(prepareData()),
    headers: {
      Accept: "application/json, text/plain, */*",
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
  });
  console.log(await response.json());
};
dataSubmissionBtn.addEventListener("click", submitData);
