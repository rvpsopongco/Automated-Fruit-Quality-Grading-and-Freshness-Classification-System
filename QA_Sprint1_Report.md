# QA Report: Sprint 1

**Project:** Automated Fruit Quality Grading and Freshness Classification System
**Course:** CPE178P Foundations of AI
**Prepared by:** Richard Von Sopongco (Quality Assurance Engineer)
**Application tested:** Streamlit frontend at `http://localhost:8501`, FastAPI backend on port 8000

---

## 1. Scope

This report covers (a) a check that the project can be set up and run by following the group's startup tutorial, and (b) functional testing of the running application with seven sample images. No source code was changed during this QA pass.

## 2. Setup verification

| Tutorial step | Result |
|---------------|--------|
| 1. Clone the repository | Worked as written |
| 2. Place `fruit_model.onnx` in `models/` beside `labels.json` | Worked as written |
| 3. Create the environment and install dependencies | Worked as written |
| 4. Start the backend (`uvicorn backend.main:app --reload --port 8000`) | Worked as written; the terminal reported the ONNX model and labels loaded |
| 5. Start the frontend (`streamlit run app.py`) | Worked as written; the app opened at `localhost:8501` |

**Conclusion:** The startup tutorial worked as written. No setup defects were found.

## 3. Functional test results

Test images: `sample fruits for live demo/` (7 images). Each image was uploaded through the UI and classified with the "Classify Fruit Quality" button.

| # | Image | Description | Expected | Actual (label, confidence) | Result |
|---|-------|-------------|----------|----------------------------|--------|
| 1 | `apple1.jpg` | Two fresh red apples on a tree | Fresh apple | FRESH, `Freshapples`, 98.20% | Pass |
| 2 | `apple2.jpg` | Shriveled, brown apple | Rotten apple | ROTTEN, `Rottenapples`, 100.00% | Pass |
| 3 | `banana1.jpg` | Yellow bananas with a few spots | Fresh banana | FRESH, `Freshbanana`, 100.00% | Pass |
| 4 | `banana2.jpg` | Dark, overripe bananas with a watermark | Rotten banana | ROTTEN, `Rottenbanana`, 99.89% | Pass |
| 5 | `orange1.jpg` | Fresh oranges on a plate | Fresh orange | FRESH, `Freshoranges`, 100.00% | Pass |
| 6 | `orange2.jpg` | Dull, spotted, shriveled orange | Rotten orange | ROTTEN, `Rottenoranges`, 100.00% | Pass |
| 7 | `apple3.jpg` | Sliced apple (edge case) | Not reliable (training data has whole fruit only) | ROTTEN, `Rottenoranges`, 47.85% | Fail (known limitation) |

**Summary:** 6 of 7 tests passed. All six whole-fruit images were classified correctly. The one failure is the sliced apple, which is the out-of-distribution case already documented in the team's AI disclosure (Log Entry 03).

## 4. Observations

1. The model misclassified sliced fruit in both freshness and fruit type: a fresh, sliced apple was labeled “Rottenoranges” with only 47.85% confidence. This matches the known limitation that the model was trained exclusively on whole fruit images. The lower confidence in this out-of-distribution case stands in contrast to the high confidence (98.20%–100.00%) given to all whole-fruit images.
2. Multiple predictions showed 100.00% confidence (tests 2, 3, 5, 6), indicating possible model overconfidence. High confidence values should not be interpreted as proof of correctness; further evaluation metrics and calibration are recommended.
3. The model demonstrated strong performance and reliability on whole, clearly presented fruits, successfully distinguishing between fresh and rotten samples for apples, bananas, and oranges.
4. For ambiguous or edge-case images (like the sliced apple), the model’s confidence dropped significantly, providing a useful signal for flagging uncertain classifications in the UI.
5. The current implementation assigns a single label per image, which is sufficient for single-fruit images but limits utility for images containing multiple distinct fruits or ambiguous cases.
6. The model’s categorical outputs match the expected classes, and there were no mislabelings among the whole-fruit images tested, supporting the correctness of label mapping and data consistency.
7. No crashes, exceptions, or visible errors occurred during classification or UI use for any of the tested sample images, indicating application stability for the tested workflow.



## 5. Link to the Sprint 2 plan

The team's Sprint 2 priorities are Docker containerization, object detection and localization, and comprehensive evaluation metrics. The QA findings above support each one:

| Sprint 2 priority | Supporting QA finding |
|-------------------|-----------------------|
| Containerization with Docker (FastAPI backend and Streamlit frontend in docker-compose) | Setup in Sprint 1 needed several manual steps: cloning, downloading the model from the shared drive, creating an environment, installing dependencies (including extra image-codec packages), and starting two services in separate terminals. Containers would remove these steps and host-environment differences. |
| Object detection and localization | Test 7 (sliced apple) failed in both freshness and fruit type, and tests 1, 3, and 5 contain several fruits but receive a single label. Detecting and cropping each fruit before grading addresses both cases. |
| Evaluation metrics (confusion matrices, per-class F1, latency benchmarks) | Seven manual tests cannot measure overall accuracy. Several outputs show 100.00% confidence (tests 2, 3, 5, 6), so held-out evaluation is needed to check whether the model's confidence is reliable. |

### Additional QA recommendations

- Integrate a user-facing warning in the UI when classification confidence falls below a defined threshold (e.g., under 70%), as low confidence correlated with the known failure on the sliced apple test.
- Expand the test set to include more edge cases, such as partially occluded fruits, mixed-quality fruits in one image, and images under varied lighting conditions, to better assess real-world performance.
- Include automated tests for non-fruit images and unsupported file types to verify that the system gracefully handles invalid inputs.
- Add robustness checks for backend availability and error handling to ensure the frontend provides clear feedback if the backend is unreachable or fails during inference.
- Maintain the current set of sample images as a regression suite and use them to validate model and pipeline changes in future sprints.



## 6. Conclusion

The application successfully ran end-to-end following the startup tutorial, and the model correctly classified all whole-fruit samples with high confidence and no software errors. The single misclassification on a sliced apple confirms a documented model limitation and highlights the need for further training on diverse data or the integration of object detection as planned for Sprint 2. No code modifications were necessary during this QA pass. These results provide a stable foundation for the next development sprint, with clear, actionable insights for model and system improvements.
