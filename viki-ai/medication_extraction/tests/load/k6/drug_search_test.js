import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  // stages: [
  //   { duration: '10s', target: 40 }, // Ramp up to 20 virtual users
  //   { duration: '60s', target: 40 }, // Stay at 20 virtual users for 30 seconds
  //   { duration: '10s', target: 0 },  // Ramp down to 0 virtual users
  // ],
  scenarios: {
    steady_rate: {
      executor: 'constant-arrival-rate',
      rate: 67, // 100 iterations per minute for 1500 meds/min.  67 for 1000 med/min
      timeUnit: '1m', // Time unit for the rate
      duration: '3m', // Test duration
      preAllocatedVUs: 10, // Pre-allocate up to 10 virtual users
      maxVUs: 150, // Maximum number of virtual users
    },
    // constant_throughput: {
    //   executor: 'constant-vus',
    //   vus: 25, // Number of virtual users
    //   duration: '3m', // Test duration
    // },
  },
};

export default function () {
  const url = `https://ai-medication-extraction-18900418456.us-east4.run.app/api/medispan/loadtest/poke?search_strategy=alloydb`;
  const params = {
    headers: {
      'Foo': `Bar`,
    },
    timeout: "300s",
  };
  //console.log(`Request URL: ${url}`); // Output the URL to the console
  let res = http.get(url, params);

  //console.log(`Response status: ${res.status}`);
  //console.log(`Response body: ${res.body}`);
  
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  
  sleep(1);
}
