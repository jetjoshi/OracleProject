/**
 * @license
 * Copyright (c) 2014, 2023, Oracle and/or its affiliates.
 * Licensed under The Universal Permissive License (UPL), Version 1.0
 * as shown at https://oss.oracle.com/licenses/upl/
 * @ignore
 */
import * as AccUtils from "../accUtils";
import * as ko from "knockout";
import { whenDocumentReady } from "ojs/ojbootstrap";
import { InputSearchElement } from "ojs/ojinputsearch";
import { ItemContext } from "ojs/ojcommontypes";
import "ojs/ojknockout";
import "ojs/ojinputsearch";
import ArrayDataProvider = require("ojs/ojarraydataprovider");
import "ojs/ojtable"; 

class DashboardViewModel {

  // Add the properties for oj-input-search values
  readonly value = ko.observable();
  readonly rawValue = ko.observable();
  readonly searchTerm = ko.observable();
  readonly searchItemContext = ko.observable();
  readonly previousSearchTerm = ko.observable();
  readonly searchTimeStamp = ko.observable();
  readonly dataProvider = ko.observable();
  private arrayDataProvider: any;
  

  constructor() {
    // Initialize oj-input-search properties
    this.value = ko.observable();
    this.rawValue = ko.observable();
    this.searchTerm = ko.observable();
    this.searchItemContext = ko.observable();
    this.previousSearchTerm = ko.observable();
    this.searchTimeStamp = ko.observable();
    this.dataProvider(this.arrayDataProvider);
    

  }

  // Change the type of 'detail' to 'InputSearchElement.ojValueAction<null, null>'
  // Original method to handle oj-input-search value action event
  handleValueAction = async (event: InputSearchElement.ojValueAction<null, null>) => {
    const detail = event.detail;
    // Call the new method with detail.value
    await this.handleValueActionHelper(detail.value);
  };

  // New method to handle the POST request
  private handleValueActionHelper = async (query: string | undefined) => {
    try {
      // Make a POST request using fetch
      const response = await fetch('http://127.0.0.1:8080/restaurant/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query || "", // Use an empty string if query is undefined
        }),
      });

      // Check if the request was successful (status code 2xx)
      if (response.ok || response.statusText == 'OK') {
        
        const jsonResponse = await response.json();
        console.log(jsonResponse);
        this.arrayDataProvider = new ArrayDataProvider(jsonResponse, {
        keyAttributes: "name",
        implicitSort: [{ attribute: "name", direction: "ascending" }],
    });

    if (this.dataProvider() === this.arrayDataProvider) {
      // The dataProvider has the data within arrayDataProvider
      console.log("dataProvider has the data");
    } else {
      // The dataProvider does not have the data within arrayDataProvider
      console.log("dataProvider does not have the data");
    }
    console.log(this.arrayDataProvider)
    console.log(this.dataProvider)
      
      }
    } catch (error) {
      console.error('Error during POST request:', error);
    }
  };
  


 




  /**
   * Optional ViewModel method invoked after the View is inserted into the
   * document DOM.
   */
  connected(): void {
    

    // Trigger the new method with an empty string
    this.handleValueActionHelper("");
    
    // Apply bindings for oj-input-search
    const containerDivElement = document.getElementById("containerDiv")!;
    if (!ko.dataFor(containerDivElement)) {
      // Apply bindings for oj-input-search only if not applied already
      whenDocumentReady().then(() => {
        ko.applyBindings(this, containerDivElement);
      });
    }

    // Other logic if needed...
  }


    // Other ViewModel methods...
  }

export = DashboardViewModel;
