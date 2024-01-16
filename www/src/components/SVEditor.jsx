import CodeMirror from '@uiw/react-codemirror';
import {historyField} from '@codemirror/commands';
import {loadLanguage} from "@uiw/codemirror-extensions-langs";


import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import * as React from "react";
import editorConfig from "./editorConfig.json";
import {Alert} from "@mui/material";


export default function SVEditor(props) {
    return (
        <Grid item xs={12} lg={6}>
            <Paper sx={editorConfig.paperConfig}>
                <Typography variant="h5">SV Code</Typography><br/>
                {
                    props.loading ? (
                        <><br/><Alert severity="info">Loading SV Code...</Alert> </>
                    ) : (
                        <CodeMirror
                            value={props.value}

                            minHeight={editorConfig.editorHeight.min}
                            maxHeight={editorConfig.editorHeight.max}

                            editable={false}
                            extensions={[loadLanguage("verilog")]}
                            basicSetup={editorConfig.basicSetup}
                        />
                    )
                }
            </Paper>
        </Grid>
    );
}
