<?php
/*
Template Name: Saints Readings 9 (SQLite)
*/
/**
 * The template for displaying daily Saints and Readings
 *
 * @link https://developer.wordpress.org/themes/basics/template-hierarchy/#single-post
 *
 * @package St_Constantine2
 */

 // Load jQuery datepicker.
 //   <b><blockquote> for TODAY...&#160;&#160;&#160;or&#160;&#160;<input type="text" class="datepicker" name="mydate" value = " Select Date" size = 12>

 if (!function_exists('wpse_enqueue_datepicker')) {
    function wpse_enqueue_datepicker() {
        // Load the datepicker script (pre-registered in WordPress).
        wp_enqueue_script( 'jquery-ui-datepicker' );

        // You need styling for the datepicker. For simplicity I've linked to Google's hosted jQuery UI CSS.
        wp_register_style( 'jquery-ui', 'http://code.jquery.com/ui/1.11.2/themes/smoothness/jquery-ui.css' );
        wp_enqueue_style( 'jquery-ui' );
    }
    add_action( 'wp_enqueue_scripts', 'wpse_enqueue_datepicker' );
}

get_header();

?>
  	<div id="primary" class="content-area">
   <main id="main" class="site-main" role="main">
   <form action="" method="post" id="d-form">
   <h2>Saints and Readings</h2>
   <b><blockquote> for TODAY...&#160;&#160;&#160;or&#160;&#160;<input type="text" class="datepicker" name="mydate" value = " Select Date" size = 12>
</blockquote></b>
        </form>
         <script>
         jQuery(function() {
             jQuery( ".datepicker" ).datepicker({
                  dateFormat : "yy-mm-dd",
                  onSelect : function() {
                         jQuery('#d-form').submit();
                  }
             });
         });
         </script> 
  
<?php

        $upload_dir = wp_upload_dir();
        $upload_path = $upload_dir['basedir'];
        $yocal_db_path = $upload_path . '/yocal/YOCal_Master.db';

        // FUNCTION TO RETURN FULL ROW OF DATA FOR A GIVEN DATE
        // ==================================================== 
        if (!function_exists('read_data')) {
    function read_data($d) {
        global $yocal_db_path;
        try {
            $db = new SQLite3($yocal_db_path, SQLITE3_OPEN_READONLY);
            $stmt = $db->prepare('SELECT * FROM yocal_main WHERE date = :date');
            $stmt->bindValue(':date', $d, SQLITE3_TEXT);
            $result = $stmt->execute();
            $row = $result->fetchArray(SQLITE3_ASSOC);
            $db->close();
            return (object)$row;
        } catch (Exception $e) {
            echo $e->getMessage() . "\n";
            return null;
        }
    }
}

if (!function_exists('read_lect')) {
    function read_lect($c) {
        global $yocal_db_path;
        try {
            $db = new SQLite3($yocal_db_path, SQLITE3_OPEN_READONLY);
            $stmt = $db->prepare('SELECT * FROM yocal_lections WHERE code = :code');
            $stmt->bindValue(':code', $c, SQLITE3_TEXT);
            $result = $stmt->execute();
            $row = $result->fetchArray(SQLITE3_ASSOC);
            $db->close();
            return (object)$row;
        } catch (Exception $e) {
            return null;
        }
    }
}

if (!function_exists('format_data')) {
    function format_data($r)   {
       // Set variables for each field of data:
       $day_name = $r->day_name;
       $day_num = $r->day_num;
       $day_ord = $r->ord;
       $month_name = $r->month;
       $year = $r->year;
       $fast = $r->fast;
       $tone = $r->tone;
       $eoth = $r->eothinon;
       $desig_a = $r->desig_a;
       $desig_g = $r->desig_g;
       $major = $r->major_commem;
       $foreafter = $r->fore_after;
       $basil = $r->basil;
       $global = $r->class_5;
       $british = $r->british;
       
       // Date in full:

       $txt1 = '<h2 class="lectionary-single-header">'.$day_name.' '.$day_ord.' '.$month_name.' '.$year.'</h2>';

       // Fasting, Tone, Eothinon, Liturgy of St Basil:
   
       $txt2 = '';

       if (strlen($fast)>1) {
          $txt2 = $fast."<br>";
       }
    
       if (strlen($tone)>1) {
          $txt2 .= $tone." - ".$eoth."<br>";
       }
    
       if (strlen($basil)>1) {
          $txt2 .= $basil."<br>";
       }    

       if (strlen($txt2)>1) {
          $txt2 = '<h4 class="lectionary-single-subtitle">'.$txt2.'</h4>';
       }  
      
       // Designations, Major Commemorations, Fore- and After-feasts:
   
       $txt3 = '';

       if (strlen($desig_a)>1) {
          $txt3 = $desig_a;
          if (strlen($desig_g)>1) {
             $txt3 .= ", ".$desig_g;
          }
          $txt3 .= "<br>";
       }
   
       if (strlen($major)>1) {
          $txt3 .= $major."<br>";
       }

       if (strlen($foreafter)>1) {
          $txt3 .= $foreafter."<br>";
       }
   
       if (strlen($txt3)>1) {
          $txt3 = '<h3 class="lectionary-single-subtitle">'.$txt3."</h3>";
       }
   
       // Minor commemorations including those of Britain and Ireland:
 
       $txt4 = '<em>Today we commemorate:</em><br>'.$global.'<br>';
 
       if (strlen($british)>1) {
          $txt4 .= '<em>British Isles and Ireland: </em><br>'.$british.'<br>';
       }

       $txt4 = '<p class="lectionary-single-saints">'.$txt4. '</p>';

 
       // Return the assembled text
  
       $text = $txt1.$txt2.$txt3.$txt4;

       return $text;
    }
}

if (!function_exists('format_lect')) {
    function format_lect($l)   {
       if (!$l) {
            return "";
       }
       // $lects is for the list of lection references
       // $texts is for the full text of the readings 
 
       $lects = "<em>Today&#39;s Readings:</em><br>";
       $texts = "";

       // Set variables for each field of data:

       $a_code = $l->a_code;
       $g_code = $l->g_code;
       if ($g_code == $a_code) {
           $g_code = "";
       }
       $is_apos = $l->is_comm_apos;
       $is_gosp = $l->is_comm_gosp;
       $c_code = $l->c_code;
       $x_code = $l->x_code;           


 
       // Get data for each code in turn: Apostle, Gospel, Extra and Commemoration

       if (strlen($a_code)>1) {
           $a_data = read_lect($a_code);
           if ($a_data) {
                $a_lect_1 = $a_data->lect_1;
                $a_lect_2 = $a_data->lect_2;
                $a_text_1 = $a_data->text_1;
                $a_text_2 = $a_data->text_2;
           }
       }

       // Deal with F7EC where only the Apostlereading is used
       if ($a_code == "F7EC") {
           $a_lect_2 = "";
           $a_text_2 = "";
       }

       if (strlen($g_code)>1) {
           $g_data = read_lect($g_code);
           if ($g_data) {
                $g_lect_2 = $g_data->lect_2;
                $g_text_2 = $g_data->text_2;
           }
       }
       if (strlen($x_code)>1) {
           $x_data = read_lect($x_code);
           if ($x_data) {
                $x_lect_1 = $x_data->lect_1;
                $x_lect_2 = $x_data->lect_2;
                $x_text_1 = $x_data->text_1;
                $x_text_2 = $x_data->text_2;
           }
       } 
       if (strlen($c_code)>1) {
           $c_data = read_lect($c_code);
           if ($c_data) {
                $c_lect_1 = $c_data->lect_1;
                $c_lect_2 = $c_data->lect_2;
                $c_text_1 = $c_data->text_1;
                $c_text_2 = $c_data->text_2;
           }
       }

       // If there is a commemoration, embolden the primary readings 
       // If no commemoration, embolden the readings of the day 

       if (strlen($c_code)>1) {  
           if ($is_apos == 1) {
              $c_lect_1 = "<b>".$c_lect_1."</b>";
           } else {
              $a_lect_1 = "<b>".$a_lect_1."</b>";
           } 
           if ($is_gosp == 1) {
              $c_lect_2 = "<b>".$c_lect_2."</b>";
           } elseif (strlen($a_lect_2)>1) {
              $a_lect_2 = "<b>".$a_lect_2."</b>";
           } elseif (strlen($g_lect_2)>1) {
              $g_lect_2 = "<b>".$g_lect_2."</b>"; 
           } 
       } else {
           $a_lect_1 = "<b>".$a_lect_1."</b>";
           if (strlen($a_lect_2)>1) {
              $a_lect_2 = "<b>".$a_lect_2."</b>";
           } elseif (strlen($g_lect_2)>1) {
              $g_lect_2 = "<b>".$g_lect_2."</b>"; 
           }
       }    

       // Assemble the various Lections and Texts

       if (strlen($a_lect_1)>1) {
           $lects .= $a_lect_1;
           $texts .= $a_text_1;
           if ((strlen($a_lect_2)>1) or (strlen($g_code)>1)) {
              $lects .= "; ";
           } else {
              $lects .= "<br>";
           }
       }
       if (strlen($a_lect_2)>1) {
           $lects .= $a_lect_2."<br>";
           $texts .= $a_text_2;
       }
       if (strlen($g_lect_2)>1) {
           $lects .= $g_lect_2."<br>";
           $texts .= $g_text_2;
       }
       if (strlen($c_lect_1)>1) {
           $lects .= "<em>For the Commemoration: </em>".$c_lect_1."; ".$c_lect_2."<br>";
           $texts .= $c_text_1.$c_text_2;
       }
       if (strlen($x_lect_1)>1) {
           $lects .= $x_lect_1;
           $texts .= $x_text_1;      
           if (strlen($x_lect_2)>1) {
              $lects .= "; ".$x_lect_2."<br>";
              $texts .= $x_text_2;
           } else {
              $lects .= "<br>";
           }
       }

       // As there is no Liturgy Mon-Fri in Lent, or on Holy Saturday, or on Wed and Fri of Cheesefare Week remove the bold tags from the lections

       if ((substr($a_code,0,1) == "G") and ((substr($a_code,2,1) != "S") or ($a_code == "G7Sat")) or ($a_code == "E36Wed") or ($a_code == "E36Fri")) {
            $lects = str_replace("<b>","",$lects);
            $lects = str_replace("</b>","",$lects);
            $lects .= '<br>';
       } else {
            $lects .= '<br><em>Readings in <b>bold type</b> are those appointed by the Typikon for use at the Liturgy</em><br>';
       }

       // Add two line breaks before each reading

       //$texts = str_replace("<em>","<br><br><em>",$texts);

       // Then remove them from the first reading

       //$texts = substr($texts,8);

       // Finally, return the assembled Lections and Texts
           
       $rtn = $lects."<br>".$texts."<br><br>";
       return $rtn;
    }
}


        // CALL THE FUNCTIONS TO DISPLAY DATA FOR A GIVEN DAY
        // ==================================================
     
        $date = $_POST["mydate"];
        if (empty($date)) {
             $date = date("Y-m-d");
        }
        $ret = read_data($date);
        $data = format_data($ret);
        $data2 = format_lect($ret);
        $data3 = $ret->explanatory_notes;

        echo $data;
        echo $data2;
	    if (!empty($data3)) {
			echo "\n<hr>\n".$data3."<br/>\n";
		}

  ?>
       

		</main><!-- #main -->
	</div><!-- #primary -->

<?php
//get_sidebar();
get_footer();
