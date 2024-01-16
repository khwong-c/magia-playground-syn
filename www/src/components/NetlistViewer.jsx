import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import * as React from "react";

import editorConfig from './editorConfig.json';
import {Alert, Button, FormControl, MenuItem, Select} from "@mui/material";

import tempScheme from './tempScheme.json';
import {useEffect} from "react";
import {AddIcCall} from "@mui/icons-material";


export default function NetlistViewer(props) {
    const netlists = props.netlist;
    const [selectedNetlist, setSelectedNetlist] = React.useState(props.top);
    useEffect(() => {
        setSelectedNetlist(props.top)
    }, [props.netlist]);
    return (
        <Grid item xs={12} lg={6}>
            <Paper sx={editorConfig.paperConfig}>
                <Grid container width={"100%"} justifyContent="space-between"
                      alignItems="center">
                    <Grid item xs={5}>
                        <Typography variant="h5">Netlist</Typography>
                    </Grid>
                    <Grid item xs={5} sx={{textAlign: 'right'}}>
                        <FormControl fullWidth>
                            <Select
                                color="primary"
                                placeholder="Select a netlist"
                                value={selectedNetlist}
                                onChange={(e) => {
                                    setSelectedNetlist(e.target.value);
                                }}
                            >
                                {
                                    Object.keys(netlists).map(
                                        (netList) => (
                                            <MenuItem key={netList} value={netList}>{netList}</MenuItem>
                                        )
                                    )
                                }
                            </Select>

                        </FormControl>

                    </Grid>
                    <Grid item xs={2} sx={{textAlign: 'right', alignContent: 'center'}}>
                        <Button
                            variant="contained" color="primary" disabled={!Object.keys(props.netlist).length}
                            onClick={(e) => {
                                const image = new Image();
                                image.src="data:image/svg+xml," + encodeURIComponent(netlists[selectedNetlist]);
                                const w = window.open("", "_blank")
                                w.document.write(image.outerHTML)
                            }}
                        >
                            Open
                        </Button>
                    </Grid>
                    <Grid item xs={12}>
                        {
                            props.loading ? (
                                <><br/><Alert severity="info">Loading Netlist...</Alert> </>
                            ) : (
                                props.err ? (
                                    <><br/><Alert severity="error">Error: {props.err}</Alert></>
                                ) : (
                                    Object.keys(props.netlist).length ? (<img
                                        src={"data:image/svg+xml," + encodeURIComponent(netlists[selectedNetlist])}
                                        alt="placeholder"
                                        className={"netlist"}
                                        width={"100%"}

                                    />) : (
                                        <><br/><Alert severity="warning">Elaborate Code for Netlist</Alert> </>
                                    )
                                )
                            )
                        }
                    </Grid>
                </Grid>

            </Paper>
        </Grid>
    );
}
