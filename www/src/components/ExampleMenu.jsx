import * as React from 'react';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import ListSubheader from '@mui/material/ListSubheader';
import AssignmentIcon from '@mui/icons-material/Assignment';

import magiaExamples from '../examples/magiaExamples.json';
import {PyCodeContext} from "../Contexts";

export function ExampleMenu(props) {
    const pyContext = React.useContext(PyCodeContext);
    return (
        <React.Fragment>
            <ListSubheader component="div" inset>
                Examples
            </ListSubheader>
            {
                Object.keys(magiaExamples).map((example) => {
                    return (
                        <ListItemButton key={example} value={example} onClick={(e) => {
                            pyContext.setCode(magiaExamples[example])
                        }}>
                            <ListItemIcon>
                                <AssignmentIcon/>
                            </ListItemIcon>
                            <ListItemText primary={example}/>
                        </ListItemButton>
                    );
                })
            }
        </React.Fragment>
    );
}

export default ExampleMenu;