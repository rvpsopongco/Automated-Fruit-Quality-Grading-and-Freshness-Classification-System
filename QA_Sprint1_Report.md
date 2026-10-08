# QA Report: Sprint 1

**Project:** Automated Fruit Quality Grading and Freshness Classification System
**Course:** CPE178P Foundations of AI
**Prepared by:** Richard Von Sopongco (Quality Assurance Engineer)
**Date tested:** October 8, 2026
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

1. **Sliced fruit is misclassified in both freshness and fruit type.** A fresh sliced apple was labeled `Rottenoranges` at 47.85%. This is consistent with the documented limitation that the model was trained only on whole fruit. The confidence (47.85%) was much lower than on every whole-fruit image (98.20% to 100.00%).
2. **Many predictions show 100.00% confidence** (tests 2, 3, 5, 6). This may mean the model is overconfident, so confidence should not be read as proof of correctness.
3. **File type handling.** `banana2.jpg` has a `.jpg` extension but its content is a WebP image with a transparency channel. The app accepted it and classified it correctly (99.89%), so the upload check appears to rely on the extension, not the file content.
4. **Images with several fruits** (`apple1.jpg`, `banana1.jpg`, `orange1.jpg`) were classified correctly. The model returns one label per image.
5. **Not covered in this pass:** non-fruit images, unsupported file types, and behavior when the backend is stopped.

## 5. Link to the Sprint 2 plan

The team's Sprint 2 priorities are Docker containerization, object detection and localization, and comprehensive evaluation metrics. The QA findings above support each one:

| Sprint 2 priority | Supporting QA finding |
|-------------------|-----------------------|
| Containerization with Docker (FastAPI backend and Streamlit frontend in docker-compose) | Setup in Sprint 1 needed several manual steps: cloning, downloading the model from the shared drive, creating an environment, installing dependencies (including extra image-codec packages), and starting two services in separate terminals. Containers would remove these steps and host-environment differences. |
| Object detection and localization | Test 7 (sliced apple) failed in both freshness and fruit type, and tests 1, 3, and 5 contain several fruits but receive a single label. Detecting and cropping each fruit before grading addresses both cases. |
| Evaluation metrics (confusion matrices, per-class F1, latency benchmarks) | Seven manual tests cannot measure overall accuracy. Several outputs show 100.00% confidence (tests 2, 3, 5, 6), so held-out evaluation is needed to check whether the model's confidence is reliable. |

### Additional QA recommendations

- Show a warning in the UI when top confidence is below a set threshold (for example, under 70%), since the failing case had low confidence.
- Validate uploaded files by content, not only by extension (see Observation 3).
- Add tests for non-fruit images, unsupported file types, and backend-unavailable behavior, which were not covered in Sprint 1.
- Keep the seven sample images as a small regression set and rerun them after each model or pipeline change.

## 6. Conclusion

The application ran end to end following the startup tutorial, and the model classified all whole-fruit samples correctly. The sliced-apple failure matches a known, documented limitation. No code changes were needed, so this report is the QA contribution for Sprint 1.
