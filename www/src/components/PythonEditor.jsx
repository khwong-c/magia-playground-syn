import CodeMirror from '@uiw/react-codemirror';
import {historyField} from '@codemirror/commands';
import {loadLanguage} from "@uiw/codemirror-extensions-langs";


import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import * as React from "react";

import editorConfig from './editorConfig.json';
import {Button} from "@mui/material";

import {PyCodeContext} from "../Contexts";

export default function PythonEditor(props) {
    // create a state for editor value
    const pyContext = React.useContext(PyCodeContext);
    const [serializedState, setSerializedState] = React.useState(localStorage.getItem('pythonEditorState'));
    const stateFields = {history: historyField};

    const onElaborate = props.onElaborate;

    return (
        <Grid item xs={12} lg={6}>
            <Paper sx={editorConfig.paperConfig}>
                <Grid container width={"100%"} justifyContent="space-between"
                      alignItems="flex-start">
                    <Grid item xs={10}>
                        <Typography variant="h5">Python Code</Typography><br/>
                    </Grid>
                    <Grid item xs={2} sx={{textAlign: 'right'}}>
                        <Button variant="contained" color="primary" onClick={(e) => {
                            onElaborate(pyContext.code)
                        }}>Elaborate</Button>
                    </Grid>
                </Grid>
                <CodeMirror
                    value={pyContext.code}
                    minHeight={editorConfig.editorHeight.min}
                    maxHeight={editorConfig.editorHeight.max}

                    extensions={[loadLanguage("python")]}
                    basicSetup={editorConfig.basicSetup}

                    initialState={
                        serializedState
                            ? {
                                json: JSON.parse(serializedState || ''),
                                fields: stateFields,
                            }
                            : undefined
                    }

                    onChange={(value, viewUpdate) => {
                        pyContext.setCode(value);
                        localStorage.setItem('pythonValue', value);

                        const state = viewUpdate.state.toJSON(stateFields);
                        const serializedState = JSON.stringify(state);
                        setSerializedState(serializedState);
                        localStorage.setItem('pythonEditorState', serializedState);
                    }}
                />
            </Paper>
        </Grid>
    );
}
